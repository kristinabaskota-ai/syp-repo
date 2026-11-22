from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import WantedRequest, Offer, User
from app.schemas import (
    WantedRequestCreate, WantedRequestOut, OfferCreate, OfferOut
)
from app.deps import get_current_user, require_buyer, require_seller, get_optional_current_user

router = APIRouter(prefix="/wanted", tags=["Wanted Board"])


def _to_offer_out(o: Offer) -> OfferOut:
    return OfferOut(
        id=o.id,
        request_id=o.request_id,
        seller_id=o.seller_id,
        seller_name=o.seller.full_name if o.seller else None,
        price=o.price,
        message=o.message,
        status=o.status,
        created_at=o.created_at,
    )


def _to_wanted_out(req: WantedRequest, current_user: Optional[User] = None) -> WantedRequestOut:
    offers_out = None
    if current_user:
        if current_user.role == "admin" or current_user.id == req.buyer_id:
            # Buyer or Admin sees all offers
            offers_out = [_to_offer_out(o) for o in req.offers]
        elif current_user.role == "seller":
            # Seller sees ONLY their own offer
            offers_out = [_to_offer_out(o) for o in req.offers if o.seller_id == current_user.id]

    return WantedRequestOut(
        id=req.id,
        buyer_id=req.buyer_id,
        buyer_name=req.buyer.full_name if req.buyer else None,
        plant_name=req.plant_name,
        destination_country=req.destination_country,
        details=req.details,
        status=req.status,
        created_at=req.created_at,
        updated_at=req.updated_at,
        offers=offers_out,
    )


@router.get("", response_model=List[WantedRequestOut])
def list_wanted_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(WantedRequest)
    if status_filter:
        query = query.filter(WantedRequest.status == status_filter)
    requests = query.order_by(WantedRequest.id.desc()).all()
    return [_to_wanted_out(r, current_user=current_user) for r in requests]


@router.post("", response_model=WantedRequestOut, status_code=status.HTTP_201_CREATED)
def create_wanted_request(
    req_in: WantedRequestCreate,
    current_user: User = Depends(require_buyer),
    db: Session = Depends(get_db)
):
    req = WantedRequest(
        buyer_id=current_user.id,
        plant_name=req_in.plant_name,
        destination_country=req_in.destination_country,
        details=req_in.details,
        status="open",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return _to_wanted_out(req, current_user=current_user)


@router.get("/{request_id}", response_model=WantedRequestOut)
def get_wanted_request(
    request_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    req = db.query(WantedRequest).filter(WantedRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wanted request not found")
    return _to_wanted_out(req, current_user=current_user)


@router.patch("/{request_id}/close", response_model=WantedRequestOut)
def close_wanted_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    req = db.query(WantedRequest).filter(WantedRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wanted request not found")

    if current_user.role != "admin" and req.buyer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only close your own requests")

    req.status = "closed"
    db.commit()
    db.refresh(req)
    return _to_wanted_out(req, current_user=current_user)


@router.post("/{request_id}/offers", response_model=OfferOut, status_code=status.HTTP_201_CREATED)
def make_offer(
    request_id: int,
    offer_in: OfferCreate,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db)
):
    req = db.query(WantedRequest).filter(WantedRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wanted request not found")

    if req.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot make offers on a '{req.status}' wanted request.",
        )

    # Rule: approved sellers send one offer per request
    existing_offer = db.query(Offer).filter(
        Offer.request_id == request_id,
        Offer.seller_id == current_user.id
    ).first()
    if existing_offer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted an offer for this request.",
        )

    offer = Offer(
        request_id=request_id,
        seller_id=current_user.id,
        price=offer_in.price,
        message=offer_in.message,
        status="pending",
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return _to_offer_out(offer)


@router.get("/{request_id}/offers", response_model=List[OfferOut])
def get_request_offers(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    req = db.query(WantedRequest).filter(WantedRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wanted request not found")

    if current_user.role == "admin" or current_user.id == req.buyer_id:
        return [_to_offer_out(o) for o in req.offers]

    if current_user.role == "seller":
        return [_to_offer_out(o) for o in req.offers if o.seller_id == current_user.id]

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.post("/{request_id}/offers/{offer_id}/accept", response_model=WantedRequestOut)
def accept_offer(
    request_id: int,
    offer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    req = db.query(WantedRequest).filter(WantedRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wanted request not found")

    if current_user.role != "admin" and req.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the buyer who posted this request can accept an offer.",
        )

    if req.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot accept an offer for a request that is not open.",
        )

    target_offer = db.query(Offer).filter(
        Offer.id == offer_id,
        Offer.request_id == request_id
    ).first()
    if not target_offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found for this request")

    # Mark target offer as accepted
    target_offer.status = "accepted"

    # Mark all other offers as rejected
    for o in req.offers:
        if o.id != offer_id:
            o.status = "rejected"

    # Mark request as fulfilled
    req.status = "fulfilled"
    db.commit()
    db.refresh(req)
    return _to_wanted_out(req, current_user=current_user)
