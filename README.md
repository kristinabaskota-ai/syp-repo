# RareRoot 🌿 — Botanical Marketplace & Plant Health Platform

**RareRoot** is a full-stack web marketplace and diagnostic web application developed for the university **BSc Hons Computing (Second Year Project, IIC)**. The platform solves two core problems faced by botanical collectors, nurseries, and plant hobbyists:
1. **Sourcing rare and exotic plants internationally with confidence regarding phytosanitary and CITES regulations.**
2. **Accurately diagnosing and safely treating plant diseases without requiring specialized horticultural degrees or risking the health of domestic pets, young children, or edible crops.**

- **Default Currency**: Nepalese Rupee (`NPR`)
- **Default Origin / Jurisdiction**: Nepal
- **Single-Address Serving**: Entire web application runs from `http://127.0.0.1:8000`

---

## ⚡ Quick Start

### Option A: Windows (One-Click)
Double-click `run.bat` in the project root folder. This batch script automatically:
1. Creates a Python virtual environment (`.venv`) if not present.
2. Activates the virtual environment.
3. Copies `backend/.env.example` to `backend/.env` if not already present.
4. Installs/verifies all dependencies from `backend/requirements.txt`.
5. Launches the FastAPI server at `http://127.0.0.1:8000`.
6. Opens your default web browser directly to `http://127.0.0.1:8000/app/index.html`.

### Option B: macOS / Linux
Open a terminal in the project root directory and execute:
```bash
chmod +x run.sh
./run.sh
```

### Option C: Manual Terminal Execution (VS Code)
1. Open the repository root or open a terminal inside the `backend` folder:
```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies (no compilers needed):
pip install -r requirements.txt

# Start application server:
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
2. Open your browser and navigate to: **`http://127.0.0.1:8000`** (auto-redirects to `/app/index.html`).

> **Live Server Note**: The frontend JavaScript (`frontend/js/api.js`) automatically detects the current port. If you open `frontend/index.html` with VS Code Live Server on port `5500`, it seamlessly proxies all API calls to `http://127.0.0.1:8000`.

---

## 🔑 Pre-Seeded Demo Accounts

The database seeds automatically on first startup with realistic demo accounts. You can also click the quick-fill chips on the sign-in page to populate these instantly:

| Role | Email Address | Password | Account Status & Notes |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@rareroot.com` | `Admin@12345` | Full administrative privileges, user vetting, rules management, sales analytics. |
| **Plant Seller (Nursery)** | `seller@rareroot.com` | `Seller@12345` | **Himalayan Flora Nursery** (pre-approved). Manages listings, receives orders, makes offers. |
| **Plant Buyer (Collector)** | `buyer@rareroot.com` | `Buyer@12345` | **Aarav Sharma**. Add to cart, checkout, order tracking, wanted board, Plant Doctor. |

---

## 📋 Role-Based Access Permission Matrix

Server-side FastAPI dependencies enforce permissions on **every single request**, querying the database directly so role modifications or deactivations take effect immediately:

| Feature / Resource | Anonymous | Buyer | Seller (Approved) | Administrator |
| :--- | :---: | :---: | :---: | :---: |
| Browse & Search Catalogue | ✅ | ✅ | ✅ | ✅ |
| Filter by Light / Pets / Tree Purpose | ✅ | ✅ | ✅ | ✅ |
| Import Biosecurity Document Checker | ✅ | ✅ | ✅ | ✅ |
| Consult Plant Doctor | ✅ | ✅ | ✅ | ✅ |
| Self-Registration (`buyer` or `seller`) | ✅ | — | — | — |
| Shopping Cart & Quantity Merging | ❌ (401) | ✅ | ❌ (403) | ❌ (403) |
| Transactional Checkout & Buy-Now | ❌ (401) | ✅ | ❌ (403) | ❌ (403) |
| View Own Purchases | ❌ (401) | ✅ | ❌ (403) | ✅ |
| Cancel Pending Order (Restores Stock) | ❌ (401) | ✅ (Pending only) | ❌ (403) | ✅ |
| Post & Close Wanted Plant Requests | ❌ (401) | ✅ | ❌ (403) | ✅ |
| Accept Offers on Own Wanted Requests | ❌ (401) | ✅ | ❌ (403) | ✅ |
| Create / Edit Own Product Listings | ❌ (401) | ❌ (403) | ✅ (Own only) | ✅ (All) |
| Hide / Delete Own Listings (Soft-Delete) | ❌ (401) | ❌ (403) | ✅ (Own only) | ✅ (All) |
| View Received Orders (Only Own Items) | ❌ (401) | ❌ (403) | ✅ | ✅ (All) |
| Advance Order Status (`pending` &rarr; `deliv`) | ❌ (401) | ❌ (403) | ✅ | ✅ |
| Submit Offer on Wanted Requests (Max 1) | ❌ (401) | ❌ (403) | ✅ | ✅ |
| User Management (Approve/Role/Status) | ❌ (401) | ❌ (403) | ❌ (403) | ✅ (No self-mod) |
| Manage Import Regulations (CRUD) | ❌ (401) | ❌ (403) | ❌ (403) | ✅ |
| View Analytics & Sales Telemetry | ❌ (401) | ❌ (403) | ❌ (403) | ✅ |

---

## 🌿 Core Features

1. **Multi-Criteria Plant Catalogue**: Public listing of verified specimens. Search by common or scientific names; filter by category (*Rare, Indoor, Seasonal, Tree, Treatment*), light requirement (*low, medium, bright, full-sun*), pet safety, and tree purpose (*fruit, shade, timber, ornamental*).
2. **Nursery Listings Management**: Approved sellers create, update, and hide listings. If a product is present in past customer orders, deletion is safely soft-handled by deactivating the listing (`is_active = False`) so customer invoices and accounting history remain immutable.
3. **Buyer Shopping Cart**: Cart merges identical items, strictly validates quantities against available live stock, and displays subtotal calculations.
4. **Atomic Checkout & "Buy Now"**: Validates entire cart stock in a single transactional unit, deducts inventory, creates immutable order item snapshots (name & price at purchase time), and clears the cart.
5. **Strict Order State Machine**: Orders move sequentially: `pending` &rarr; `confirmed` &rarr; `shipped` &rarr; `delivered`. Skips are rejected. Buyers can cancel while `pending`, automatically returning reserved stock to store inventory.
6. **Wanted Plant Board**: Collectors broadcast coveted plant requests. Approved nurseries submit competitive offers (limit 1 per nursery). The buyer reviews offers and accepts the winning bid, which fulfills the request and automatically rejects competing offers.
7. **Import Biosecurity & CITES Checker**: Aggregates general destination rules with matching target species. Features an amber warning for CITES-listed plants (e.g., *Orchids, Paphiopedilum, Cycads, Cacti*), a red alert for banned invasive species (e.g., *Water Hyacinth* in the US and Australia), a biosecurity advisory for unregistered countries, and a legal disclaimer.
8. **AI-Assisted Plant Doctor (Main Innovation)**: Guided 3-step diagnostic flow:
   - Step 1: Plant Part (*leaf, stem, root, flower*).
   - Step 2: Observed symptom.
   - Step 3: Household safety switches (*domestic pets, young children, edible crops*).
   - Remedies ranked: **Organic first (1)**, then **Non-chemical (2)**, then **Chemical (3)**. Unsafe treatments are filtered out with an exact count of hidden options. If all remedies are unsafe for the household, users receive advice to consult a local nursery.
   - Remedies link to purchasable treatment products in the shop with a one-click "Add to Cart" button.
   - Diagnostic consultations are saved to user history.
   - **Architectural Hook**: The diagnostic engine is fully decoupled into `run_diagnosis()`, designed so a future MobileNetV2 image classification model only outputs a `symptom_id` without altering safety or ranking logic.
9. **Platform Administration**: User management table (role adjustment, nursery approval, activation toggle with self-deactivation protection), import regulations CRUD manager, and platform analytics reports (total sales volume excluding cancelled orders, orders by status, user breakdown, top products, common diagnoses, low-stock inventory alerts).
10. **Account Security**: Update profile name, change password with current password verification (automatically revokes JWT to end active session), forgot password with single-use 15-minute SHA-256 tokens.

---

## 🧪 Automated Testing Suite

The project includes **54 automated unit and integration tests** utilizing `pytest` and `httpx.TestClient` against an in-memory SQLite database:

```bash
# Run test suite from the backend directory:
cd backend
python -m pytest -v
```

### Test Coverage Highlights:
- **`test_auth.py`** (16 tests): Buyer/seller registration, rejection of self-registered admin, case-insensitive duplicate email checks, password strength rules, JWT issuance, 5-attempt login lockout (HTTP 429), token blacklist revocation upon logout, password change and reset token workflows.
- **`test_permissions.py`** (8 tests): Strict enforcement of all 401/403 permission boundaries for Anonymous, Buyer, Seller, and Admin roles, seller approval checks, and admin self-deactivation guard.
- **`test_products.py`** (8 tests): Search, multi-attribute filtering, seller CRUD, toggle-active, hard deletion vs. soft-hiding when orders exist.
- **`test_cart.py`** (3 tests): Adding, updating, stock limit validation, and cart clearing.
- **`test_orders.py`** (5 tests): Transactional stock deduction, Buy-Now flow, sequential status enforcement (no skipping), stock restoration upon cancellation, and prohibition of cancelling confirmed orders.
- **`test_wanted.py`** (2 tests): Request posting, single-offer limit per seller, offer acceptance, competing offer rejection, request closing.
- **`test_import_check.py`** (6 tests): Country rules aggregation, CITES alerts, banned weed warnings, unknown country fallbacks, legal disclaimer presence, and admin CRUD.
- **`test_doctor.py`** (5 tests): Anatomical part filtering, organic-first ranking, pet safety filters, linked shop product rendering, and diagnostic history recording.
- **`test_reports.py`** (1 test): Sales volume calculation (excluding cancelled orders), order status breakdown, user counts, top products, and low-stock telemetry.

---

## 📦 What is NOT Built (Explicit Assumptions)

In compliance with project specifications for this 2nd-year academic prototype:
1. **Real Payment Gateways**: Real financial transactions (eSewa, Khalti, Stripe) are not integrated. The checkout flow simulates instantaneous transactional stock reservation and creates verified order records.
2. **Trained Image Classification Weights**: Real-time photo upload with a live-trained MobileNetV2 model is not yet bundled. The system provides a clinical guided diagnostic wizard and is architecturally pre-hooked (`run_diagnosis`) for seamless model integration.
3. **Live SMTP Mail Server**: External email sending is not configured. When testing forgot/reset password in development mode (`DEV_RETURN_RESET_TOKEN=true`), the single-use reset token is printed to the console and returned directly in the response for instantaneous testing.
4. **Regulatory & Medical Data Note**: All import rules, biosecurity documents, CITES appendix ratings, and treatment safety flags are **SAMPLE DATA** provided for educational demonstrations.

---

## 🛠️ Git & Version Control Instructions

To push this codebase to a GitHub repository:
```bash
# Initialize git repository
git init

# Stage all files
git add .

# Create initial commit
git commit -m "feat: complete RareRoot botanical marketplace application with Plant Doctor and import checker"

# Rename default branch to main
git branch -M main

# Add your GitHub remote repository URL
git remote add origin https://github.com/<your-username>/RareRoot.git

# Push code to remote repository
git push -u origin main
```

---

## 📚 Technical Documentation

Additional diagrams generated with Mermaid formatting:
- [`docs/ERD.md`](docs/ERD.md): Complete Entity Relationship Diagram mapping all 14 database models and relationships.
- [`docs/USE_CASES.md`](docs/USE_CASES.md): Use case diagrams and matrix for Visitor, Buyer, Seller, and Admin actors.
- [`docs/WBS.md`](docs/WBS.md): Hierarchical Work Breakdown Structure.
- [`docs/GANTT.md`](docs/GANTT.md): Project development schedule from October 2026 to March 2027.
