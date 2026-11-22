import pytest
from app.models import User, TokenBlacklist, PasswordResetToken


def test_register_buyer_success(client):
    resp = client.post("/auth/register", json={
        "full_name": "New Buyer",
        "email": "newbuyer@example.com",
        "password": "Password123",
        "role": "buyer"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newbuyer@example.com"
    assert data["role"] == "buyer"
    assert data["is_approved"] is True
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_seller_starts_unapproved(client):
    resp = client.post("/auth/register", json={
        "full_name": "New Seller Nursery",
        "email": "newseller@example.com",
        "password": "Password123",
        "role": "seller"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["role"] == "seller"
    assert data["is_approved"] is False


def test_register_admin_rejected(client):
    resp = client.post("/auth/register", json={
        "full_name": "Hacker Admin",
        "email": "hacker@example.com",
        "password": "Password123",
        "role": "admin"
    })
    assert resp.status_code == 422 or resp.status_code == 400


def test_register_duplicate_email_rejected(client):
    resp = client.post("/auth/register", json={
        "full_name": "Duplicate User",
        "email": "buyer@rareroot.com",
        "password": "Password123",
        "role": "buyer"
    })
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"].lower()


def test_register_case_insensitive_email(client):
    resp = client.post("/auth/register", json={
        "full_name": "Case User",
        "email": "BUYER@RAREROOT.COM",
        "password": "Password123",
        "role": "buyer"
    })
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"].lower()


@pytest.mark.parametrize("bad_password,expected_error", [
    ("short1", "between 8 and 64"),
    ("allletterslowercase", "at least one number"),
    ("1234567890", "at least one letter"),
])
def test_register_password_strength_validation(client, bad_password, expected_error):
    resp = client.post("/auth/register", json={
        "full_name": "Weak User",
        "email": f"weak_{bad_password}@example.com",
        "password": bad_password,
        "role": "buyer"
    })
    assert resp.status_code == 422


def test_login_success_json(client):
    resp = client.post("/auth/login", json={
        "email": "buyer@rareroot.com",
        "password": "Buyer@12345"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "buyer@rareroot.com"


def test_login_success_form_token(client):
    resp = client.post("/auth/token", data={
        "username": "buyer@rareroot.com",
        "password": "Buyer@12345"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_invalid_password_and_invalid_email_return_same_message(client):
    # Wrong password
    resp1 = client.post("/auth/login", json={
        "email": "buyer@rareroot.com",
        "password": "WrongPassword123"
    })
    assert resp1.status_code == 401

    # Wrong email
    resp2 = client.post("/auth/login", json={
        "email": "nonexistent@rareroot.com",
        "password": "WrongPassword123"
    })
    assert resp2.status_code == 401

    assert resp1.json()["detail"] == resp2.json()["detail"]
    assert resp1.json()["detail"] == "Invalid email or password"


def test_login_lockout_after_five_failed_attempts(client):
    # Register isolated user to test lockout
    client.post("/auth/register", json={
        "full_name": "Lockout Test",
        "email": "lockout@example.com",
        "password": "Password123",
        "role": "buyer"
    })

    # 4 failed attempts: returns 401
    for _ in range(4):
        resp = client.post("/auth/login", json={"email": "lockout@example.com", "password": "WrongPassword1"})
        assert resp.status_code == 401

    # 5th failed attempt: triggers lockout
    resp5 = client.post("/auth/login", json={"email": "lockout@example.com", "password": "WrongPassword1"})
    assert resp5.status_code == 401

    # 6th attempt: should return 429 Too Many Requests
    resp6 = client.post("/auth/login", json={"email": "lockout@example.com", "password": "Password123"})
    assert resp6.status_code == 429
    assert "locked" in resp6.json()["detail"].lower()


def test_logout_revokes_token(client, buyer_headers):
    # Verify token works first
    resp1 = client.get("/users/me", headers=buyer_headers)
    assert resp1.status_code == 200

    # Call logout
    resp_logout = client.post("/auth/logout", headers=buyer_headers)
    assert resp_logout.status_code == 200
    assert resp_logout.json()["message"] == "Logged out successfully"

    # Next call with same token must fail with 401 (revoked)
    resp2 = client.get("/users/me", headers=buyer_headers)
    assert resp2.status_code == 401
    assert "revoked" in resp2.json()["detail"].lower()


def test_change_password_success_and_ends_session(client):
    # Register dedicated user
    client.post("/auth/register", json={
        "full_name": "Change Pass User",
        "email": "changepass@example.com",
        "password": "OldPassword123",
        "role": "buyer"
    })
    login_resp = client.post("/auth/login", json={"email": "changepass@example.com", "password": "OldPassword123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Change password
    change_resp = client.post("/auth/change-password", headers=headers, json={
        "current_password": "OldPassword123",
        "new_password": "NewPassword456"
    })
    assert change_resp.status_code == 200

    # Session token should now be revoked
    check_resp = client.get("/users/me", headers=headers)
    assert check_resp.status_code == 401

    # Login with new password works
    new_login = client.post("/auth/login", json={"email": "changepass@example.com", "password": "NewPassword456"})
    assert new_login.status_code == 200


def test_change_password_with_incorrect_current_password(client, buyer_headers):
    resp = client.post("/auth/change-password", headers=buyer_headers, json={
        "current_password": "WrongCurrentPassword123",
        "new_password": "ValidNewPassword456"
    })
    assert resp.status_code == 400
    assert "incorrect current password" in resp.json()["detail"].lower()


def test_forgot_password_and_reset_flow(client):
    # Register user
    client.post("/auth/register", json={
        "full_name": "Reset User",
        "email": "resetme@example.com",
        "password": "InitialPassword123",
        "role": "buyer"
    })

    # Forgot password for registered email
    resp1 = client.post("/auth/forgot-password", json={"email": "resetme@example.com"})
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert "reset_token" in data1
    reset_token = data1["reset_token"]

    # Forgot password for non-existent email returns same public message
    resp2 = client.post("/auth/forgot-password", json={"email": "nonexistent_reset@example.com"})
    assert resp2.status_code == 200
    assert resp2.json()["message"] == data1["message"]

    # Reset password with valid token
    reset_resp = client.post("/auth/reset-password", json={
        "token": reset_token,
        "new_password": "UpdatedPassword789"
    })
    assert reset_resp.status_code == 200

    # Reusing the same token fails
    reuse_resp = client.post("/auth/reset-password", json={
        "token": reset_token,
        "new_password": "AnotherPassword123"
    })
    assert reuse_resp.status_code == 400
    assert "invalid or expired" in reuse_resp.json()["detail"].lower()

    # Login with new password works
    login_resp = client.post("/auth/login", json={"email": "resetme@example.com", "password": "UpdatedPassword789"})
    assert login_resp.status_code == 200
