# RareRoot - Project Schedule (Gantt Chart)

This timeline details the engineering milestones spanning **October 2026 to March 2027** for the BSc Hons Computing Second Year Project.

```mermaid
gantt
    title RareRoot Project Implementation Timeline (Oct 2026 - Mar 2027)
    dateFormat  YYYY-MM-DD
    axisFormat  %b %Y

    section 1. Planning & Design
    Project Proposal & Scope Alignment      :done,    p1, 2026-10-01, 2026-10-18
    Literature Review & Biosecurity Research:done,    p2, 2026-10-15, 2026-10-31
    Domain Modeling & ERD Specification    :done,    p3, 2026-10-25, 2026-11-10
    UI/UX Design & Botanical Palette Guide  :done,    p4, 2026-11-01, 2026-11-15

    section 2. Backend Engineering
    FastAPI Core Setup & Security Subsystem :done,    b1, 2026-11-10, 2026-11-25
    Catalogue, Cart & Checkout APIs         :done,    b2, 2026-11-20, 2026-12-10
    Wanted Board & Seller Offer System      :done,    b3, 2026-12-05, 2026-12-22
    Import Document Checker & CITES Engine  :done,    b4, 2026-12-18, 2027-01-08
    Plant Doctor Symptom Pathology Engine   :done,    b5, 2027-01-02, 2027-01-22
    Admin Telemetry & Reporting Endpoints   :done,    b6, 2027-01-15, 2027-01-30

    section 3. Frontend Development
    Responsive App Shell & Hash Routing     :active,  f1, 2027-01-15, 2027-02-05
    Storefront, Filters & Modal Views       :active,  f2, 2027-01-25, 2027-02-15
    Plant Doctor 3-Step Guided Wizard       :active,  f3, 2027-02-05, 2027-02-22
    Seller Nursery & Admin Workspaces       :         f4, 2027-02-12, 2027-02-28

    section 4. AI Model Exploration
    Dataset Curation (Plant Village)        :         ai1, 2027-02-01, 2027-02-15
    MobileNetV2 Transfer Learning Prototype :         ai2, 2027-02-15, 2027-03-05

    section 5. Testing & Delivery
    Pytest Suite Expansion (54+ Tests)      :         q1, 2027-02-20, 2027-03-10
    Security Audit (Lockout, JWT, RBAC)     :         q2, 2027-03-01, 2027-03-15
    Final Academic Report & Submission      :crit,    q3, 2027-03-10, 2027-03-25
```

## Milestone Deadlines

- **Milestone 1 (End of Nov 2026)**: Backend core architecture, database migrations, authentication, and security foundation complete.
- **Milestone 2 (End of Dec 2026)**: Marketplace catalogue, cart, transactional checkout, and Wanted Board operational.
- **Milestone 3 (End of Jan 2027)**: Plant Doctor clinical symptom diagnostic engine, CITES import checker, and admin analytics completed.
- **Milestone 4 (Mid Feb 2027)**: Frontend integration complete, zero-build single address serving at `http://127.0.0.1:8000`.
- **Milestone 5 (March 2027)**: Complete test verification (all 54 tests passing), cross-platform documentation, final university project defense.
