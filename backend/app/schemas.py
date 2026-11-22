from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from app.security import validate_password_strength


# --- User Schemas ---
class UserRegister(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str
    role: Literal["buyer", "seller"] = "buyer"

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        is_valid, msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(msg)
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    is_approved: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)


class UserRoleUpdate(BaseModel):
    role: Literal["buyer", "seller", "admin"]


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserApproveUpdate(BaseModel):
    is_approved: bool


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def check_password(cls, v: str) -> str:
        is_valid, msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(msg)
        return v


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def check_password(cls, v: str) -> str:
        is_valid, msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(msg)
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --- Category Schemas ---
class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- Product Schemas ---
class ProductCreate(BaseModel):
    category_id: int
    name: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=5)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    light_requirement: Literal["low", "medium", "bright", "full-sun"]
    pet_safe: bool = False
    tree_purpose: Optional[Literal["fruit", "shade", "timber", "ornamental", "none"]] = None
    image_url: Optional[str] = None
    is_active: bool = True


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, min_length=5)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    light_requirement: Optional[Literal["low", "medium", "bright", "full-sun"]] = None
    pet_safe: Optional[bool] = None
    tree_purpose: Optional[Literal["fruit", "shade", "timber", "ornamental", "none"]] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ProductOut(BaseModel):
    id: int
    seller_id: int
    category_id: int
    name: str
    description: str
    price: float
    stock: int
    light_requirement: str
    pet_safe: bool
    tree_purpose: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category_name: Optional[str] = None
    seller_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- Cart Schemas ---
class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(1, gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    product: ProductOut
    item_total: float

    model_config = ConfigDict(from_attributes=True)


class CartSummaryOut(BaseModel):
    items: List[CartItemOut]
    total: float
    currency: str = "NPR"


# --- Order Schemas ---
class CheckoutRequest(BaseModel):
    shipping_address: str = Field(..., min_length=5)
    destination_country: str = Field(default="Nepal", min_length=2)


class BuyNowRequest(BaseModel):
    product_id: int
    quantity: int = Field(1, gt=0)
    shipping_address: str = Field(..., min_length=5)
    destination_country: str = Field(default="Nepal", min_length=2)


class OrderItemOut(BaseModel):
    id: int
    product_id: Optional[int]
    product_name: str
    unit_price: float
    quantity: int
    subtotal: float

    model_config = ConfigDict(from_attributes=True)


class OrderOut(BaseModel):
    id: int
    user_id: int
    status: str
    total: float
    shipping_address: str
    destination_country: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemOut]
    buyer_name: Optional[str] = None
    buyer_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: Literal["confirmed", "shipped", "delivered"]


# --- Wanted Board Schemas ---
class WantedRequestCreate(BaseModel):
    plant_name: str = Field(..., min_length=2, max_length=255)
    destination_country: str = Field(default="Nepal", min_length=2)
    details: str = Field(..., min_length=5)


class OfferCreate(BaseModel):
    price: float = Field(..., gt=0)
    message: str = Field(..., min_length=5)


class OfferOut(BaseModel):
    id: int
    request_id: int
    seller_id: int
    seller_name: Optional[str] = None
    price: float
    message: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WantedRequestOut(BaseModel):
    id: int
    buyer_id: int
    buyer_name: Optional[str] = None
    plant_name: str
    destination_country: str
    details: str
    status: str
    created_at: datetime
    updated_at: datetime
    offers: Optional[List[OfferOut]] = None

    model_config = ConfigDict(from_attributes=True)


# --- Import Checker Schemas ---
class ImportRuleCreate(BaseModel):
    country: str = Field(..., min_length=2, max_length=100)
    plant_name: str = Field(default="*", min_length=1, max_length=255)
    required_documents: str = Field(..., min_length=2)
    is_banned: bool = False
    cites_protected: bool = False
    notes: Optional[str] = None


class ImportRuleUpdate(BaseModel):
    country: Optional[str] = None
    plant_name: Optional[str] = None
    required_documents: Optional[str] = None
    is_banned: Optional[bool] = None
    cites_protected: Optional[bool] = None
    notes: Optional[str] = None


class ImportRuleOut(BaseModel):
    id: int
    country: str
    plant_name: str
    required_documents: str
    is_banned: bool
    cites_protected: bool
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ImportCheckResponse(BaseModel):
    country: str
    plant_name: str
    country_found: bool
    is_banned: bool
    cites_protected: bool
    required_documents: List[str]
    matched_rules: List[ImportRuleOut]
    notes: List[str]
    disclaimer: str


# --- Plant Doctor Schemas ---
class SymptomOut(BaseModel):
    id: int
    plant_part: str
    observation: str
    diagnosis: str
    cause: str

    model_config = ConfigDict(from_attributes=True)


class TreatmentOut(BaseModel):
    id: int
    symptom_id: int
    name: str
    treatment_type: str
    pet_safe: bool
    child_safe: bool
    edible_safe: bool
    instructions: str
    product_id: Optional[int] = None
    product: Optional[ProductOut] = None

    model_config = ConfigDict(from_attributes=True)


class DiagnosisRequest(BaseModel):
    symptom_id: int
    has_pets: bool = False
    has_children: bool = False
    plant_is_edible: bool = False


class DiagnosisResponse(BaseModel):
    diagnosis_id: Optional[int] = None
    symptom: SymptomOut
    total_treatments: int
    hidden_treatments_count: int
    household_advice: Optional[str] = None
    safe_treatments: List[TreatmentOut]


class DiagnosisHistoryOut(BaseModel):
    id: int
    symptom_id: int
    plant_part: str
    observation: str
    diagnosis: str
    cause: str
    has_pets: bool
    has_children: bool
    plant_is_edible: bool
    created_at: datetime


# --- Admin Reports Schemas ---
class TopProductReport(BaseModel):
    product_id: Optional[int]
    product_name: str
    total_quantity_sold: int
    total_revenue: float


class CommonDiagnosisReport(BaseModel):
    symptom_id: int
    plant_part: str
    observation: str
    diagnosis: str
    count: int


class AdminReportOut(BaseModel):
    total_sales: float
    orders_by_status: Dict[str, int]
    users_by_role: Dict[str, int]
    top_products: List[TopProductReport]
    common_diagnoses: List[CommonDiagnosisReport]
    low_stock_count: int
    low_stock_products: List[ProductOut]
