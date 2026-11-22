import { productsApi, getCurrentUser, escapeHtml } from "../api.js";
import { openModal, closeModal, showToast, confirmDialog } from "../app.js";

export async function renderListingsView(container) {
  const user = getCurrentUser();
  const isAdmin = user && user.role === "admin";

  container.innerHTML = `
    <div class="section-header">
      <div>
        <h2 class="section-title">${isAdmin ? "Platform Listings Management" : "My Nursery Listings"}</h2>
        <p class="section-subtitle">${isAdmin ? "Manage all seller listings across the RareRoot platform." : "Create and update your botanical store inventory and availability."}</p>
      </div>
      <div>
        <button class="btn btn-primary" id="addNewListingBtn">
          + Add New Plant Listing
        </button>
      </div>
    </div>

    <!-- Listings Table Container -->
    <div class="table-container" id="listingsTableArea">
      <div class="empty-state">
        <p>Loading your botanical inventory...</p>
      </div>
    </div>
  `;

  const listingsTableArea = document.getElementById("listingsTableArea");
  const addNewListingBtn = document.getElementById("addNewListingBtn");

  async function loadListings() {
    listingsTableArea.innerHTML = `<div class="empty-state"><p>Loading inventory...</p></div>`;
    try {
      const products = await productsApi.getSellerProducts();

      if (!products || products.length === 0) {
        listingsTableArea.innerHTML = `
          <div class="empty-state">
            <div class="empty-state-icon">🏷️</div>
            <h3>No listings created yet</h3>
            <p>Publish your first plant specimen to make it discoverable on the marketplace.</p>
          </div>
        `;
        return;
      }

      const fallbackImg = "https://images.unsplash.com/photo-1545241047-6083a3684587?w=600&auto=format&fit=crop&q=80";

      const rowsHtml = products.map(p => `
        <tr data-id="${p.id}">
          <td style="width: 60px;">
            <img src="${escapeHtml(p.image_url || fallbackImg)}" alt="${escapeHtml(p.name)}" style="width: 44px; height: 44px; border-radius: var(--radius-sm); object-fit: cover;" onerror="this.src='${fallbackImg}'">
          </td>
          <td>
            <strong style="color: var(--primary-dark); font-size: 0.95rem;">${escapeHtml(p.name)}</strong>
            ${isAdmin ? `<div style="font-size: 0.78rem; color: var(--text-muted);">Seller: ${escapeHtml(p.seller_name || 'Nursery')}</div>` : ''}
          </td>
          <td>
            <span class="badge badge-${(p.category_name || 'rare').toLowerCase()}">${escapeHtml(p.category_name || 'Plant')}</span>
          </td>
          <td>
            <div style="font-weight: 700; color: var(--primary);">NPR ${p.price.toLocaleString()}</div>
          </td>
          <td>
            <span style="font-weight: 600; ${p.stock === 0 ? 'color: var(--danger);' : (p.stock <= 5 ? 'color: var(--warning);' : 'color: var(--success);')}">
              ${p.stock} units
            </span>
          </td>
          <td>
            <button class="btn btn-sm ${p.is_active ? 'btn-outline' : 'btn-secondary'} toggle-active-btn" data-id="${p.id}" style="font-size: 0.75rem; padding: 0.2rem 0.6rem;">
              ${p.is_active ? '● Active (Visible)' : '○ Hidden'}
            </button>
          </td>
          <td style="text-align: right;">
            <button class="btn btn-secondary btn-sm edit-listing-btn" data-id="${p.id}" style="margin-right: 0.35rem;">
              Edit
            </button>
            <button class="btn btn-secondary btn-sm delete-listing-btn" data-id="${p.id}" style="color: var(--danger);">
              Delete
            </button>
          </td>
        </tr>
      `).join("");

      listingsTableArea.innerHTML = `
        <table class="data-table">
          <thead>
            <tr>
              <th>Image</th>
              <th>Specimen</th>
              <th>Category</th>
              <th>Price</th>
              <th>Stock</th>
              <th>Storefront Status</th>
              <th style="text-align: right;">Actions</th>
            </tr>
          </thead>
          <tbody>
            ${rowsHtml}
          </tbody>
        </table>
      `;

      // Bind toggle active
      listingsTableArea.querySelectorAll(".toggle-active-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
          const prodId = btn.dataset.id;
          try {
            await productsApi.toggleActive(prodId);
            showToast("Listing visibility toggled.", "info");
            await loadListings();
          } catch (err) {
            showToast(err.message, "error");
          }
        });
      });

      // Bind edit
      listingsTableArea.querySelectorAll(".edit-listing-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const prodId = btn.dataset.id;
          const prod = products.find(p => p.id == prodId);
          if (prod) showListingModal(prod);
        });
      });

      // Bind delete
      listingsTableArea.querySelectorAll(".delete-listing-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const prodId = btn.dataset.id;
          const prod = products.find(p => p.id == prodId);
          confirmDialog(
            "Delete Listing?",
            `Are you sure you want to remove "${prod ? prod.name : 'this item'}"? Note: If this product exists in past orders, it will be automatically hidden to preserve audit records.`,
            async () => {
              try {
                const res = await productsApi.deleteProduct(prodId);
                showToast(res.message, "info");
                await loadListings();
              } catch (err) {
                showToast(err.message, "error");
              }
            }
          );
        });
      });

    } catch (err) {
      listingsTableArea.innerHTML = `
        <div class="empty-state">
          <p style="color: var(--danger);">Failed to load listings: ${escapeHtml(err.message)}</p>
        </div>
      `;
    }
  }

  async function showListingModal(prod = null) {
    const isEdit = prod !== null;
    let categories = [];
    try {
      categories = await productsApi.getCategories();
    } catch (e) {
      // ignore
    }

    const catOptions = categories.map(c => `
      <option value="${c.id}" ${prod && prod.category_id === c.id ? 'selected' : ''}>${escapeHtml(c.name)}</option>
    `).join("");

    openModal(`
      <div class="modal-header">
        <h3 class="modal-title font-serif">${isEdit ? 'Edit Plant Listing' : 'Add New Plant Listing'}</h3>
        <button class="modal-close-btn" data-close-modal>&times;</button>
      </div>
      <form id="listingForm">
        <div class="modal-body">
          <div class="form-group">
            <label for="listingName">Plant Name</label>
            <input type="text" id="listingName" class="form-input" value="${prod ? escapeHtml(prod.name) : ''}" placeholder="e.g. Philodendron Florida Beauty" required minlength="2">
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label for="listingCategory">Category</label>
              <select id="listingCategory" class="form-select" required>
                ${catOptions}
              </select>
            </div>
            <div class="form-group">
              <label for="listingLight">Light Requirement</label>
              <select id="listingLight" class="form-select" required>
                <option value="low" ${prod && prod.light_requirement === 'low' ? 'selected' : ''}>Low Light</option>
                <option value="medium" ${prod && prod.light_requirement === 'medium' ? 'selected' : ''}>Medium Light</option>
                <option value="bright" ${prod && prod.light_requirement === 'bright' ? 'selected' : ''}>Bright Indirect</option>
                <option value="full-sun" ${prod && prod.light_requirement === 'full-sun' ? 'selected' : ''}>Full Sun</option>
              </select>
            </div>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label for="listingPrice">Price (NPR)</label>
              <input type="number" id="listingPrice" class="form-input" value="${prod ? prod.price : ''}" placeholder="e.g. 3500" min="1" step="0.5" required>
            </div>
            <div class="form-group">
              <label for="listingStock">Stock Quantity</label>
              <input type="number" id="listingStock" class="form-input" value="${prod ? prod.stock : '5'}" placeholder="Units in nursery" min="0" required>
            </div>
          </div>

          <div class="form-group">
            <label for="listingDesc">Description</label>
            <textarea id="listingDesc" class="form-textarea" placeholder="Describe the plant's variegation, rooting state, pot size, and care recommendations..." required minlength="5">${prod ? escapeHtml(prod.description) : ''}</textarea>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label for="listingTreePurpose">Tree Purpose (If Tree Category)</label>
              <select id="listingTreePurpose" class="form-select">
                <option value="none">N/A (Not a tree)</option>
                <option value="fruit" ${prod && prod.tree_purpose === 'fruit' ? 'selected' : ''}>Fruit</option>
                <option value="shade" ${prod && prod.tree_purpose === 'shade' ? 'selected' : ''}>Shade</option>
                <option value="timber" ${prod && prod.tree_purpose === 'timber' ? 'selected' : ''}>Timber</option>
                <option value="ornamental" ${prod && prod.tree_purpose === 'ornamental' ? 'selected' : ''}>Ornamental</option>
              </select>
            </div>

            <div class="form-group">
              <label for="listingPetSafe">Pet Safety Certification</label>
              <select id="listingPetSafe" class="form-select">
                <option value="false" ${prod && !prod.pet_safe ? 'selected' : ''}>Non Pet Safe (Caution)</option>
                <option value="true" ${prod && prod.pet_safe ? 'selected' : ''}>🐾 Certified Pet Safe</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="listingImageUrl">Image URL (Optional)</label>
            <input type="url" id="listingImageUrl" class="form-input" value="${prod && prod.image_url ? escapeHtml(prod.image_url) : ''}" placeholder="https://images.unsplash.com/...">
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-close-modal>Cancel</button>
          <button type="submit" class="btn btn-primary" id="saveListingBtn">
            ${isEdit ? 'Save Changes' : 'Publish Listing'}
          </button>
        </div>
      </form>
    `);

    document.getElementById("listingForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        name: document.getElementById("listingName").value.trim(),
        category_id: parseInt(document.getElementById("listingCategory").value),
        light_requirement: document.getElementById("listingLight").value,
        price: parseFloat(document.getElementById("listingPrice").value),
        stock: parseInt(document.getElementById("listingStock").value),
        description: document.getElementById("listingDesc").value.trim(),
        tree_purpose: document.getElementById("listingTreePurpose").value,
        pet_safe: document.getElementById("listingPetSafe").value === "true",
        image_url: document.getElementById("listingImageUrl").value.trim() || null,
      };

      const saveBtn = document.getElementById("saveListingBtn");
      saveBtn.disabled = true;
      saveBtn.textContent = "Saving...";

      try {
        if (isEdit) {
          await productsApi.updateProduct(prod.id, payload);
          showToast("Listing updated successfully!", "success");
        } else {
          await productsApi.createProduct(payload);
          showToast("Plant listing published to shop!", "success");
        }
        closeModal();
        await loadListings();
      } catch (err) {
        showToast(err.message, "error");
        saveBtn.disabled = false;
        saveBtn.textContent = isEdit ? "Save Changes" : "Publish Listing";
      }
    });
  }

  addNewListingBtn.addEventListener("click", () => showListingModal());

  await loadListings();
}
