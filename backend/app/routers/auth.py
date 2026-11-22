from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User, TokenBlacklist, PasswordResetToken
from app.schemas import (
    UserRegister, UserLogin, UserOut, TokenResponse,
    PasswordChange, ForgotPasswordRequest, ResetPasswordRequest
)
from app.security import (
    verify_password, get_password_hash, create_access_token,
    decode_access_token, generate_reset_token, hash_reset_token
)
from app.deps import get_current_user, oauth2_scheme

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    if user_in.role not in ("buyer", "seller"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Self-registration is only allowed for 'buyer' or 'seller' roles.",
        )

    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # New sellers start unapproved until an administrator approves them
    is_approved = True if user_in.role == "buyer" else False

    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        is_active=True,
        is_approved=is_approved,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def _authenticate_and_create_token(email: str, password: str, db: Session) -> TokenResponse:
    now = datetime.now(timezone.utc)
    email_clean = email.strip().lower()

    user = db.query(User).filter(User.email == email_clean).first()

    # Check lockout
    if user and user.locked_until:
        # Normalize locked_until to timezone aware if naive
        locked_dt = user.locked_until
        if locked_dt.tzinfo is None:
            locked_dt = locked_dt.replace(tzinfo=timezone.utc)
        if locked_dt > now:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Account locked due to too many failed login attempts. Try again in 15 minutes.",
            )
        else:
            # Lockout expired, reset attempts
            user.locked_until = None
            user.failed_login_attempts = 0
            db.commit()

    if not user or not verify_password(password, user.hashed_password):
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = now + timedelta(minutes=15)
            db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact support.",
        )

    # Reset failed attempts upon successful authentication
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()

    access_token, jti = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login_json(credentials: UserLogin, db: Session = Depends(get_db)):
    return _authenticate_and_create_token(credentials.email, credentials.password, db)


@router.post("/token", response_model=TokenResponse)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Form data username field contains the email
    return _authenticate_and_create_token(form_data.username, form_data.password, db)


@router.post("/logout")
def logout(
    token: Optional[str] = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_access_token(token)
    if not payload or "jti" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    jti = payload["jti"]
    exp_timestamp = payload.get("exp")
    if exp_timestamp:
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    else:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Blacklist the token jti
    existing_entry = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
    if not existing_entry:
        blacklist_item = TokenBlacklist(jti=jti, expires_at=expires_at)
        db.add(blacklist_item)
        db.commit()

    return {"message": "Logged out successfully"}


@router.post("/change-password")
def change_password(
    data: PasswordChange,
    token: Optional[str] = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()

    # Invalidate current session token so user must re-authenticate
    if token:
        payload = decode_access_token(token)
        if payload and "jti" in payload:
            jti = payload["jti"]
            exp_timestamp = payload.get("exp")
            expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc) if exp_timestamp else datetime.now(timezone.utc) + timedelta(hours=1)
            if not db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first():
                db.add(TokenBlacklist(jti=jti, expires_at=expires_at))
                db.commit()

    return {"message": "Password changed successfully. Current session ended."}


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    raw_token = None
    if user:
        # Mark previous unused tokens as used
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.is_used == False
        ).update({"is_used": True})

        raw_token = generate_reset_token()
        hashed = hash_reset_token(raw_token)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=15)

        reset_entry = PasswordResetToken(
            user_id=user.id,
            token_hash=hashed,
            expires_at=expires_at,
            is_used=False
        )
        db.add(reset_entry)
        db.commit()

        if settings.DEV_RETURN_RESET_TOKEN:
            print(f"[DEV] Password reset token for {user.email}: {raw_token}")

    response = {
        "message": "If your email is registered, you will receive password reset instructions."
    }
    if settings.DEV_RETURN_RESET_TOKEN and raw_token:
        response["reset_token"] = raw_token

    return response


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    hashed = hash_reset_token(data.token)
    now = datetime.now(timezone.utc)

    reset_entry = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == hashed,
        PasswordResetToken.is_used == False
    ).first()

    if not reset_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    expires_at = reset_entry.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        reset_entry.is_used = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user = db.query(User).filter(User.id == reset_entry.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Associated user not found",
        )

    user.hashed_password = get_password_hash(data.new_password)
    user.failed_login_attempts = 0
    user.locked_until = None
    reset_entry.is_used = True
    db.commit()

    return {"message": "Password has been reset successfully. Please log in with your new password."}
