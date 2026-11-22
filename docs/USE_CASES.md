# RareRoot - System Use Cases

This document describes all operational use cases across the four primary system actors: **Visitor (Anonymous)**, **Buyer (Collector)**, **Seller (Approved Nursery)**, and **Administrator**.

```mermaid
flowchart LR
    subgraph Actors
        V["👤 Anonymous Visitor"]
        B["🛒 Buyer (Collector)"]
        S["🏡 Approved Seller"]
        A["🛡️ Administrator"]
    end

    subgraph "Catalogue & Compliance"
        UC1["Browse / Search Plants"]
        UC2["Filter by Light, Pets, Tree"]
        UC3["Check Import Regulations & CITES"]
        UC4["Register Account (Buyer/Seller)"]
        UC5["Log In & Lockout Protection"]
    end

    subgraph "E-Commerce & Orders"
        UC6["Manage Cart Items"]
        UC7["Atomic Stock Checkout & Buy Now"]
        UC8["View Own Order History"]
        UC9["Cancel Pending Order (Restores Stock)"]
        UC10["Manage Nursery Listings (CRUD)"]
        UC11["Process Received Orders & Advance Status"]
    end

    subgraph "Sourcing & Diagnostics"
        UC12["Post Wanted Plant Request"]
        UC13["Submit Seller Offer (Max 1)"]
        UC14["Accept Sourcing Offer"]
        UC15["Guided Plant Doctor Diagnosis"]
        UC16["Household Safety Filtering"]
        UC17["Purchase Prescribed Treatment"]
    end

    subgraph "Administration"
        UC18["Approve / Review Sellers"]
        UC19["Manage User Roles & Activation"]
        UC20["Manage Import Biosecurity Rules"]
        UC21["View Business & Diagnostic Analytics"]
    end

    V --> UC1
    V --> UC2
    V --> UC3
    V --> UC4
    V --> UC5

    B --> UC1
    B --> UC6
    B --> UC7
    B --> UC8
    B --> UC9
    B --> UC12
    B --> UC14
    B --> UC15
    B --> UC16
    B --> UC17

    S --> UC1
    S --> UC10
    S --> UC11
    S --> UC13
    S --> UC15
    S --> UC16

    A --> UC1
    A --> UC10
    A --> UC11
    A --> UC18
    A --> UC19
    A --> UC20
    A --> UC21
```

## Detailed Use Case Matrix

| ID | Use Case | Primary Actor | Pre-Conditions | Flow / Post-Condition |
| :--- | :--- | :--- | :--- | :--- |
| **UC-01** | Browse Catalogue | Visitor, Buyer, Seller, Admin | None | Searches plants by keywords; filters by category, light, pet-safety, and tree purpose. |
| **UC-02** | Check Import Rules | Visitor, Buyer, Seller, Admin | Destination country selected | Combines general rules with target species; flags CITES or banned status; shows checklist. |
| **UC-03** | User Self-Registration | Visitor | Valid email, strong password | Registers as `buyer` (auto-approved) or `seller` (starts pending review). |
| **UC-04** | User Authentication | Registered User | Active account | Exchanges credentials for JWT. Enforces 15-min lockout after 5 consecutive failed passwords. |
| **UC-05** | Add to Cart & Checkout | Buyer | Logged in as Buyer | Merges duplicate items; validates stock atomically before deducting inventory and clearing cart. |
| **UC-06** | Cancel Pending Order | Buyer | Order status is `pending` | Buyer cancels order. Order becomes `cancelled` and reserved stock returns to inventory. |
| **UC-07** | Manage Nursery Listings | Approved Seller, Admin | Seller approved | Creates, edits, and toggles active state. Soft-hides products if present in historical orders. |
| **UC-08** | Fulfill Received Orders | Seller, Admin | Order contains seller items | Advances status strictly sequentially: `pending` &rarr; `confirmed` &rarr; `shipped` &rarr; `delivered`. |
| **UC-09** | Post Wanted Plant | Buyer | Logged in as Buyer | Publishes botanical request with delivery country and required specimen traits. |
| **UC-10** | Submit Sourcing Offer | Approved Seller | Request is `open` | Submits 1 competitive price offer with plant details. |
| **UC-11** | Accept Sourcing Offer | Buyer | Owner of open request | Accepts 1 offer; request becomes `fulfilled`; competing offers are automatically rejected. |
| **UC-12** | Consult Plant Doctor | Any User | None | 3-step wizard (Part &rarr; Observation &rarr; Household flags). Filters remedies and ranks organic-first. |
| **UC-13** | User Management | Administrator | Logged in as Admin | Changes user roles, approves new nurseries, activates/deactivates accounts (self-deactivation barred). |
| **UC-14** | Import Rules Administration | Administrator | Logged in as Admin | Full CRUD for biosecurity import documentation and CITES protective restrictions. |
| **UC-15** | Platform Analytics | Administrator | Logged in as Admin | Monitors net sales volume (excludes cancelled), orders breakdown, top products, and common diagnoses. |
