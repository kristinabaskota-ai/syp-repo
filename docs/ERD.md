# RareRoot - Entity Relationship Diagram (ERD)

This document visualizes the complete database schema for the **RareRoot** botanical marketplace, covering user identity, e-commerce transactions, peer-to-peer sourcing, regulatory biosecurity compliance, and the AI-assisted Plant Doctor diagnostic engine.

```mermaid
erDiagram
    USERS ||--o{ PRODUCTS : "sells"
    USERS ||--o{ CART_ITEMS : "adds"
    USERS ||--o{ ORDERS : "places"
    USERS ||--o{ WANTED_REQUESTS : "posts"
    USERS ||--o{ OFFERS : "makes"
    USERS ||--o{ DIAGNOSES : "consults"
    USERS ||--o{ PASSWORD_RESET_TOKENS : "requests"

    CATEGORIES ||--o{ PRODUCTS : "classifies"

    PRODUCTS ||--o{ CART_ITEMS : "referenced_in"
    PRODUCTS ||--o{ ORDER_ITEMS : "ordered_in"
    PRODUCTS ||--o{ TREATMENTS : "recommends_product"

    ORDERS ||--|{ ORDER_ITEMS : "contains"

    WANTED_REQUESTS ||--o{ OFFERS : "receives"

    SYMPTOMS ||--|{ TREATMENTS : "has_remedies"
    SYMPTOMS ||--o{ DIAGNOSES : "diagnosed_in"

    USERS {
        int id PK
        string email UK
        string full_name
        string hashed_password
        string role "buyer, seller, admin"
        boolean is_active
        boolean is_approved "seller review status"
        int failed_login_attempts
        datetime locked_until
        datetime created_at
        datetime updated_at
    }

    TOKEN_BLACKLIST {
        int id PK
        string jti UK "UUID identifier"
        datetime expires_at
        datetime created_at
    }

    PASSWORD_RESET_TOKENS {
        int id PK
        int user_id FK
        string token_hash "SHA-256"
        datetime expires_at
        boolean is_used
        datetime created_at
    }

    CATEGORIES {
        int id PK
        string name UK "Rare, Indoor, Seasonal, Tree, Treatment"
        text description
    }

    PRODUCTS {
        int id PK
        int seller_id FK
        int category_id FK
        string name
        text description
        float price "NPR"
        int stock
        string light_requirement "low, medium, bright, full-sun"
        boolean pet_safe
        string tree_purpose "fruit, shade, timber, ornamental, none"
        string image_url
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    CART_ITEMS {
        int id PK
        int user_id FK
        int product_id FK
        int quantity
        datetime created_at
        datetime updated_at
    }

    ORDERS {
        int id PK
        int user_id FK
        string status "pending, confirmed, shipped, delivered, cancelled"
        float total "NPR"
        text shipping_address
        string destination_country "Default: Nepal"
        datetime created_at
        datetime updated_at
    }

    ORDER_ITEMS {
        int id PK
        int order_id FK
        int product_id FK "nullable on delete"
        string product_name "historical snapshot"
        float unit_price "historical snapshot"
        int quantity
    }

    WANTED_REQUESTS {
        int id PK
        int buyer_id FK
        string plant_name
        string destination_country
        text details
        string status "open, fulfilled, closed"
        datetime created_at
        datetime updated_at
    }

    OFFERS {
        int id PK
        int request_id FK
        int seller_id FK
        float price "NPR"
        text message
        string status "pending, accepted, rejected"
        datetime created_at
    }

    IMPORT_RULES {
        int id PK
        string country
        string plant_name "* for general rules"
        text required_documents "newline-separated"
        boolean is_banned
        boolean cites_protected
        text notes
    }

    SYMPTOMS {
        int id PK
        string plant_part "leaf, stem, root, flower"
        string observation
        string diagnosis
        text cause
    }

    TREATMENTS {
        int id PK
        int symptom_id FK
        int product_id FK "optional link to shop"
        string name
        string treatment_type "organic, non-chemical, chemical"
        boolean pet_safe
        boolean child_safe
        boolean edible_safe
        text instructions
    }

    DIAGNOSES {
        int id PK
        int user_id FK "nullable for guests"
        int symptom_id FK
        boolean has_pets
        boolean has_children
        boolean plant_is_edible
        datetime created_at
    }
```

## Schema Highlights

1. **Transactional Integrity & Audit Snapshots**:
   `ORDER_ITEMS` preserves `product_name` and `unit_price` at the moment of order placement. If a seller edits or hides a product later, historical order accounting remains strictly preserved.
2. **Soft Deletions**:
   Products referenced in past order records cannot be physically deleted; instead, they are deactivated (`is_active = False`) to maintain relational database integrity.
3. **Security State**:
   `TOKEN_BLACKLIST` ensures instant JWT invalidation upon logout or password change. `PASSWORD_RESET_TOKENS` stores single-use SHA-256 hashes with 15-minute expiration windows.
4. **Diagnostic Decoupling**:
   `SYMPTOMS` and `TREATMENTS` are isolated from machine learning dependencies, enabling plug-and-play integration for future MobileNetV2 vision models while preserving ranking logic.
