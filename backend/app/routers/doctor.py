from typing import List, Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Symptom, Treatment, Diagnosis, User
from app.schemas import (
    SymptomOut, TreatmentOut, DiagnosisRequest, DiagnosisResponse, DiagnosisHistoryOut
)
from app.deps import get_current_user, get_optional_current_user
from app.routers.products import _to_product_out

router = APIRouter(prefix="/doctor", tags=["Plant Doctor"])

# Treatment ranking preference: organic -> non-chemical -> chemical
TREATMENT_TYPE_RANK = {
    "organic": 1,
    "non-chemical": 2,
    "chemical": 3,
}


def _to_symptom_out(s: Symptom) -> SymptomOut:
    return SymptomOut(
        id=s.id,
        plant_part=s.plant_part,
        observation=s.observation,
        diagnosis=s.diagnosis,
        cause=s.cause,
    )


def _to_treatment_out(t: Treatment) -> TreatmentOut:
    prod_out = _to_product_out(t.product) if t.product and t.product.is_active else None
    return TreatmentOut(
        id=t.id,
        symptom_id=t.symptom_id,
        name=t.name,
        treatment_type=t.treatment_type,
        pet_safe=t.pet_safe,
        child_safe=t.child_safe,
        edible_safe=t.edible_safe,
        instructions=t.instructions,
        product_id=t.product_id,
        product=prod_out,
    )


def run_diagnosis(
    symptom_id: int,
    has_pets: bool,
    has_children: bool,
    plant_is_edible: bool,
    user_id: Optional[int],
    db: Session
) -> DiagnosisResponse:
    """
    Decoupled diagnostic logic.
    A future MobileNetV2 image classification pipeline can predict symptom_id from image
    features and pass directly into this function, maintaining identical household safety
    and organic-first ranking logic.
    """
    symptom = db.query(Symptom).filter(Symptom.id == symptom_id).first()
    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom not found",
        )

    all_treatments = db.query(Treatment).filter(Treatment.symptom_id == symptom_id).all()
    total_treatments = len(all_treatments)

    # Filter according to household safety requirements
    safe_treatments = []
    for t in all_treatments:
        if has_pets and not t.pet_safe:
            continue
        if has_children and not t.child_safe:
            continue
        if plant_is_edible and not t.edible_safe:
            continue
        safe_treatments.append(t)

    hidden_count = total_treatments - len(safe_treatments)

    # Rank treatments: organic first (rank 1), non-chemical (rank 2), chemical (rank 3)
    safe_treatments.sort(key=lambda t: TREATMENT_TYPE_RANK.get(t.treatment_type.lower(), 99))

    advice = None
    if len(safe_treatments) == 0:
        advice = (
            "No standard treatments meet all your specified household safety requirements. "
            "Because of sensitive household members (pets, young children, or edible crops), "
            "we strongly recommend consulting a local plant nursery or certified horticulturist "
            "for custom non-toxic remediation."
        )

    # Record diagnosis history
    diag_record = Diagnosis(
        user_id=user_id,
        symptom_id=symptom.id,
        has_pets=has_pets,
        has_children=has_children,
        plant_is_edible=plant_is_edible,
    )
    db.add(diag_record)
    db.commit()
    db.refresh(diag_record)

    return DiagnosisResponse(
        diagnosis_id=diag_record.id,
        symptom=_to_symptom_out(symptom),
        total_treatments=total_treatments,
        hidden_treatments_count=hidden_count,
        household_advice=advice,
        safe_treatments=[_to_treatment_out(t) for t in safe_treatments],
    )


@router.get("/parts", response_model=List[str])
def get_plant_parts(db: Session = Depends(get_db)):
    parts = db.query(Symptom.plant_part).distinct().all()
    return [p[0] for p in parts]


@router.get("/symptoms", response_model=List[SymptomOut])
def get_symptoms(
    plant_part: Optional[str] = Query(None, description="Filter by plant part (leaf, stem, root, flower)"),
    db: Session = Depends(get_db)
):
    query = db.query(Symptom)
    if plant_part:
        query = query.filter(Symptom.plant_part == plant_part.strip().lower())
    symptoms = query.order_by(Symptom.id.asc()).all()
    return [_to_symptom_out(s) for s in symptoms]


@router.post("/diagnose", response_model=DiagnosisResponse)
def diagnose_plant(
    diag_in: DiagnosisRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    return run_diagnosis(
        symptom_id=diag_in.symptom_id,
        has_pets=diag_in.has_pets,
        has_children=diag_in.has_children,
        plant_is_edible=diag_in.plant_is_edible,
        user_id=user_id,
        db=db,
    )


@router.get("/history", response_model=List[DiagnosisHistoryOut])
def get_diagnosis_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    diagnoses = db.query(Diagnosis).filter(
        Diagnosis.user_id == current_user.id
    ).order_by(Diagnosis.id.desc()).limit(20).all()

    result = []
    for d in diagnoses:
        symptom = d.symptom
        if symptom:
            result.append(
                DiagnosisHistoryOut(
                    id=d.id,
                    symptom_id=d.symptom_id,
                    plant_part=symptom.plant_part,
                    observation=symptom.observation,
                    diagnosis=symptom.diagnosis,
                    cause=symptom.cause,
                    has_pets=d.has_pets,
                    has_children=d.has_children,
                    plant_is_edible=d.plant_is_edible,
                    created_at=d.created_at,
                )
            )
    return result
