from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import ImportRule, User
from app.schemas import (
    ImportRuleCreate, ImportRuleUpdate, ImportRuleOut, ImportCheckResponse
)
from app.deps import require_admin

router = APIRouter(tags=["Import Document Checker"])

LEGAL_DISCLAIMER = (
    "Guidance only: This tool provides general import requirements and CITES alerts based on sample data. "
    "It does not constitute official legal advice. Biosecurity and phytosanitary rules change frequently; "
    "always verify with official government biosecurity authorities before shipping."
)


def _to_rule_out(r: ImportRule) -> ImportRuleOut:
    return ImportRuleOut(
        id=r.id,
        country=r.country,
        plant_name=r.plant_name,
        required_documents=r.required_documents,
        is_banned=r.is_banned,
        cites_protected=r.cites_protected,
        notes=r.notes,
    )


@router.get("/import-check", response_model=ImportCheckResponse)
def check_import_regulations(
    country: str = Query(..., min_length=2, description="Destination country name"),
    plant_name: Optional[str] = Query(None, description="Plant common or scientific name"),
    db: Session = Depends(get_db)
):
    country_clean = country.strip()
    plant_clean = plant_name.strip().lower() if plant_name else ""

    # Look up all rules for this country (case-insensitive)
    country_rules = db.query(ImportRule).filter(
        ImportRule.country.ilike(country_clean)
    ).all()

    if not country_rules:
        return ImportCheckResponse(
            country=country_clean,
            plant_name=plant_clean,
            country_found=False,
            is_banned=False,
            cites_protected=False,
            required_documents=[],
            matched_rules=[],
            notes=["No specific import regulations found for this country. Please consult the destination country's Ministry of Agriculture or biosecurity department."],
            disclaimer=LEGAL_DISCLAIMER,
        )

    matched_rules = []
    # 1. Add country general rules where plant_name == '*'
    general_rules = [r for r in country_rules if r.plant_name.strip() == "*"]
    matched_rules.extend(general_rules)

    # 2. Add matching plant-specific rules if plant_name provided
    if plant_clean:
        for r in country_rules:
            if r.plant_name.strip() != "*":
                r_plant = r.plant_name.strip().lower()
                # Match if plant_clean contains rule plant or rule plant contains plant_clean
                if r_plant in plant_clean or plant_clean in r_plant:
                    if r not in matched_rules:
                        matched_rules.append(r)

    # Aggregate documents, notes, and flags
    is_banned = any(r.is_banned for r in matched_rules)
    cites_protected = any(r.cites_protected for r in matched_rules)

    docs_set = []
    notes_list = []
    for r in matched_rules:
        # Split documents by newline
        lines = [line.strip() for line in r.required_documents.splitlines() if line.strip()]
        for line in lines:
            if line not in docs_set:
                docs_set.append(line)
        if r.notes and r.notes.strip() not in notes_list:
            notes_list.append(r.notes.strip())

    return ImportCheckResponse(
        country=country_clean,
        plant_name=plant_clean,
        country_found=True,
        is_banned=is_banned,
        cites_protected=cites_protected,
        required_documents=docs_set,
        matched_rules=[_to_rule_out(r) for r in matched_rules],
        notes=notes_list,
        disclaimer=LEGAL_DISCLAIMER,
    )


# --- Admin Import Rules CRUD ---
@router.get("/import-rules", response_model=List[ImportRuleOut])
def list_import_rules(
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ImportRule)
    if country:
        query = query.filter(ImportRule.country.ilike(f"%{country.strip()}%"))
    rules = query.order_by(ImportRule.country.asc(), ImportRule.plant_name.asc()).all()
    return [_to_rule_out(r) for r in rules]


@router.post("/import-rules", response_model=ImportRuleOut, status_code=status.HTTP_201_CREATED)
def create_import_rule(
    rule_in: ImportRuleCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    rule = ImportRule(
        country=rule_in.country.strip(),
        plant_name=rule_in.plant_name.strip(),
        required_documents=rule_in.required_documents.strip(),
        is_banned=rule_in.is_banned,
        cites_protected=rule_in.cites_protected,
        notes=rule_in.notes.strip() if rule_in.notes else None,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return _to_rule_out(rule)


@router.put("/import-rules/{rule_id}", response_model=ImportRuleOut)
def update_import_rule(
    rule_id: int,
    rule_in: ImportRuleUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    rule = db.query(ImportRule).filter(ImportRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import rule not found")

    update_data = rule_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if isinstance(val, str):
            val = val.strip()
        setattr(rule, field, val)

    db.commit()
    db.refresh(rule)
    return _to_rule_out(rule)


@router.delete("/import-rules/{rule_id}")
def delete_import_rule(
    rule_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    rule = db.query(ImportRule).filter(ImportRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import rule not found")

    db.delete(rule)
    db.commit()
    return {"message": "Import rule deleted successfully."}
