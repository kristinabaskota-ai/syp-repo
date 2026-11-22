import { productsApi, cartApi, ordersApi, getCurrentUser, escapeHtml } from "../api.js";
import { openModal, closeModal, showToast, updateCartBadge } from "../app.js";

export async function renderShopView(container) {
  const user = getCurrentUser();
  const isBuyer = user && user.role === "buyer";

  container.innerHTML = `
    <div class="section-header">
      <div>
        <h2 class="section-title">Plant Catalogue</h2>
        <p class="section-subtitle">Discover certified rare botanical specimens, indoor foliage, and organic remedies.</p>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="search-input-wrap">
        <input type="text" id="shopSearchInput" class="form-input" placeholder="🔍 Search plants by name or description...">
      </div>
      <div class="filter-select-wrap">
        <select id="shopCategorySelect" class="form-select">
          <option value="">All Categories</option>
        </select>
      </div>
      <div class="filter-select-wrap">
        <select id="shopLightSelect" class="form-select">
          <option value="">Any Light Level</option>
          <option value="low">Low Light</option>
          <option value="medium">Medium Light</option>
          <option value="bright">Bright Indirect</option>
          <option value="full-sun">Full Sun</option>
        </select>
      </div>
      <div class="filter-select-wrap">
        <select id="shopPetSafeSelect" class="form-select">
          <option value="">Pet Safety (All)</option>
          <option value="true">🐾 Pet Safe Only</option>
          <option value="false">Non Pet Safe</option>
        </select>
      </div>
      <div class="filter-select-wrap">
        <select id="shopTreePurposeSelect" class="form-select">
          <option value="">Tree Purpose (All)</option>
          <option value="fruit">Fruit</option>
          <option value="shade">Shade</option>
          <option value="timber">Timber</option>
          <option value="ornamental">Ornamental</option>
        </select>
      </div>
    </div>

    <!-- Products Grid -->
    <div id="shopProductsGrid" class="product-grid">
      <div class="empty-state" style="grid-column: 1 / -1;">
        <p>Loading botanical collection...</p>
      </div>
    </div>
  `;

  const productsGrid = document.getElementById("shopProductsGrid");
  const searchInput = document.getElementById("shopSearchInput");
  const categorySelect = document.getElementById("shopCategorySelect");
  const lightSelect = document.getElementById("shopLightSelect");
  const petSafeSelect = document.getElementById("shopPetSafeSelect");
  const treePurposeSelect = document.getElementById("shopTreePurposeSelect");

  // Load categories
  try {
    const categories = await productsApi.getCategories();
    categories.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = c.name;
      categorySelect.appendChild(opt);
    });
  } catch (e) {
    console.error("Failed to load categories", e);
  }

  async function loadProducts() {
    productsGrid.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <p>Loading botanical collection...</p>
      </div>
    `;

    try {
      const params = {
        search: searchInput.value.trim(),
        category_id: categorySelect.value || undefined,
        light_requirement: lightSelect.value || undefined,
        pet_safe: petSafeSelect.value !== "" ? petSafeSelect.value : undefined,
        tree_purpose: treePurposeSelect.value || undefined,
      };

      const products = await productsApi.listProducts(params);

      if (products.length === 0) {
        productsGrid.innerHTML = `
          <div class="empty-state" style="grid-column: 1 / -1;">
            <div class="empty-state-icon">🌱</div>
            <h3>No plants found</h3>
            <p>Try adjusting your search query or filters.</p>
          </div>
        `;
        return;
      }

      productsGrid.innerHTML = products.map(p => {
        const catBadgeClass = `badge-${(p.category_name || "rare").toLowerCase()}`;
        const petSafeBadge = p.pet_safe ? `<span class="badge badge-pet-safe">🐾 Pet Safe</span>` : "";
        const fallbackImg = "https://images.unsplash.com/photo-1545241047-6083a3684587?w=600&auto=format&fit=crop&q=80";
        const stockStatusClass = p.stock > 5 ? "in-stock" : (p.stock > 0 ? "low-stock" : "out-stock");
        const stockStatusText = p.stock > 5 ? `${p.stock} available` : (p.stock > 0 ? `Only ${p.stock} left!` : "Out of stock");

        return `
          <div class="product-card" data-id="${p.id}">
            <div class="product-card-img-wrap">
              <img src="${escapeHtml(p.image_url || fallbackImg)}" alt="${escapeHtml(p.name)}" class="product-card-img" onerror="this.src='${fallbackImg}'">
              <div class="product-badge-group">
                <span class="badge ${catBadgeClass}">${escapeHtml(p.category_name || "Plant")}</span>
                ${petSafeBadge}
              </div>
            </div>
            <div class="product-card-body">
              <h3 class="product-name">${escapeHtml(p.name)}</h3>
              <p class="product-desc">${escapeHtml(p.description)}</p>
              <div class="product-meta">
                <span>☀️ ${escapeHtml(p.light_requirement)}</span>
                ${p.tree_purpose ? `<span>🌳 ${escapeHtml(p.tree_purpose)}</span>` : ""}
              </div>
              <div class="product-card-footer">
                <div>
                  <div class="product-price"><span class="currency">NPR</span>${p.price.toLocaleString()}</div>
                  <div class="stock-tag ${stockStatusClass}">${stockStatusText}</div>
                </div>
                <button class="btn btn-outline btn-sm view-detail-btn" data-id="${p.id}">
                  Details
                </button>
              </div>
            </div>
          </div>
        `;
      }).join("");

      // Bind detail buttons and cards
      productsGrid.querySelectorAll(".view-detail-btn, .product-card-img-wrap, .product-name").forEach(el => {
        el.addEventListener("click", (e) => {
          const card = el.closest(".product-card");
          const prodId = card ? card.dataset.id : el.dataset.id;
          if (prodId) {
            const product = products.find(p => p.id == prodId);
            if (product) showProductModal(product);
          }
        });
      });

    } catch (err) {
      productsGrid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <div class="empty-state-icon">⚠️</div>
          <h3>Error loading plants</h3>
          <p>${escapeHtml(err.message)}</p>
        </div>
      `;
    }
  }

  function showProductModal(p) {
    const fallbackImg = "https://images.unsplash.com/photo-1545241047-6083a3684587?w=600&auto=format&fit=crop&q=80";
    const canBuy = isBuyer && p.stock > 0;

    openModal(`
      <div class="modal-header">
        <div>
          <span class="badge badge-${(p.category_name || 'rare').toLowerCase()}">${escapeHtml(p.category_name || 'Plant')}</span>
          <h3 class="modal-title font-serif" style="margin-top: 0.3rem;">${escapeHtml(p.name)}</h3>
        </div>
        <button class="modal-close-btn" data-close-modal>&times;</button>
      </div>
      <div class="modal-body" style="padding: 1.5rem;">
        <div style="height: 240px; border-radius: var(--radius-md); overflow: hidden; margin-bottom: 1.25rem;">
          <img src="${escapeHtml(p.image_url || fallbackImg)}" alt="${escapeHtml(p.name)}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='${fallbackImg}'">
        </div>
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 1rem;">
          <div class="product-price" style="font-size: 1.7rem;"><span class="currency">NPR</span>${p.price.toLocaleString()}</div>
          <div style="font-size: 0.88rem; color: var(--text-muted);">
            Seller: <strong>${escapeHtml(p.seller_name || 'Verified Nursery')}</strong>
          </div>
        </div>
        <p style="font-size: 0.95rem; line-height: 1.55; color: var(--text-primary); margin-bottom: 1.25rem;">
          ${escapeHtml(p.description)}
        </p>
        <div style="background: var(--bg-main); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 0.9rem 1.1rem; display: flex; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 1.5rem; font-size: 0.85rem;">
          <div>☀️ Light: <strong>${escapeHtml(p.light_requirement)}</strong></div>
          <div>🐾 Pet Safe: <strong>${p.pet_safe ? 'Yes (Non-toxic)' : 'Caution (Keep away from pets)'}</strong></div>
          ${p.tree_purpose ? `<div>🌳 Tree Purpose: <strong>${escapeHtml(p.tree_purpose)}</strong></div>` : ''}
          <div>📦 In Stock: <strong>${p.stock} units</strong></div>
        </div>

        ${canBuy ? `
          <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
            <label for="modalQtyInput" style="font-weight: 600; font-size: 0.9rem;">Quantity:</label>
            <input type="number" id="modalQtyInput" class="form-input" value="1" min="1" max="${p.stock}" style="width: 80px; text-align: center;">
            <span style="font-size: 0.82rem; color: var(--text-muted);">(Max ${p.stock})</span>
          </div>
        ` : (isBuyer && p.stock === 0 ? `
          <div style="padding: 0.75rem; background: var(--danger-bg); color: var(--danger); border-radius: var(--radius-sm); font-size: 0.88rem; margin-bottom: 1rem;">
            This specimen is currently sold out. Check back soon or post a request on the Wanted Board!
          </div>
        ` : `
          <div style="padding: 0.75rem; background: var(--bg-main); color: var(--text-muted); border-radius: var(--radius-sm); font-size: 0.88rem; margin-bottom: 1rem;">
            Purchasing is available for collector/buyer accounts. Log in as a buyer to purchase.
          </div>
        `)}
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" data-close-modal>Close</button>
        ${canBuy ? `
          <button class="btn btn-outline" id="modalAddToCartBtn">Add to Cart</button>
          <button class="btn btn-accent" id="modalBuyNowBtn">Buy Now</button>
        ` : ''}
      </div>
    `);

    if (canBuy) {
      const qtyInput = document.getElementById("modalQtyInput");

      document.getElementById("modalAddToCartBtn").addEventListener("click", async () => {
        const qty = parseInt(qtyInput.value) || 1;
        try {
          await cartApi.addToCart(p.id, qty);
          showToast(`Added ${qty} × ${p.name} to cart!`, "success");
          await updateCartBadge();
          closeModal();
        } catch (err) {
          showToast(err.message, "error");
        }
      });

      document.getElementById("modalBuyNowBtn").addEventListener("click", () => {
        const qty = parseInt(qtyInput.value) || 1;
        closeModal();
        showInstantCheckoutModal(p, qty);
      });
    }
  }

  function showInstantCheckoutModal(p, qty) {
    const totalAmount = roundTwoDecimals(p.price * qty);

    openModal(`
      <div class="modal-header">
        <h3 class="modal-title font-serif">Instant Checkout</h3>
        <button class="modal-close-btn" data-close-modal>&times;</button>
      </div>
      <form id="buyNowForm">
        <div class="modal-body">
          <div style="background: var(--bg-main); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 1.25rem;">
            <div style="font-weight: 700; font-size: 1.05rem;">${escapeHtml(p.name)}</div>
            <div style="display: flex; justify-content: space-between; font-size: 0.88rem; color: var(--text-muted); margin-top: 0.3rem;">
              <span>Quantity: ${qty} &times; NPR ${p.price.toLocaleString()}</span>
              <strong style="color: var(--primary); font-size: 1rem;">NPR ${totalAmount.toLocaleString()}</strong>
            </div>
          </div>

          <div class="form-group">
            <label for="buyNowAddress">Delivery Address (Street, Ward, City)</label>
            <input type="text" id="buyNowAddress" class="form-input" placeholder="e.g. Baluwatar, Ward 4, Kathmandu" required>
          </div>

          <div class="form-group">
            <label for="buyNowCountry">Destination Country</label>
            <input type="text" id="buyNowCountry" class="form-input" value="Nepal" required>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-close-modal>Cancel</button>
          <button type="submit" class="btn btn-primary" id="confirmBuyNowBtn">
            Confirm Order (NPR ${totalAmount.toLocaleString()})
          </button>
        </div>
      </form>
    `);

    document.getElementById("buyNowForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const address = document.getElementById("buyNowAddress").value.trim();
      const country = document.getElementById("buyNowCountry").value.trim();
      const submitBtn = document.getElementById("confirmBuyNowBtn");

      submitBtn.disabled = true;
      submitBtn.textContent = "Processing...";

      try {
        const order = await ordersApi.buyNow({
          product_id: p.id,
          quantity: qty,
          shipping_address: address,
          destination_country: country,
        });
        closeModal();
        showToast("Order placed successfully! Stock deducted.", "success");
        window.location.hash = "#orders";
      } catch (err) {
        showToast(err.message, "error");
        submitBtn.disabled = false;
        submitBtn.textContent = "Confirm Order";
      }
    });
  }

  function roundTwoDecimals(num) {
    return Math.round((num + Number.EPSILON) * 100) / 100;
  }

  // Filter change events
  let debounceTimer;
  searchInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(loadProducts, 300);
  });
  categorySelect.addEventListener("change", loadProducts);
  lightSelect.addEventListener("change", loadProducts);
  petSafeSelect.addEventListener("change", loadProducts);
  treePurposeSelect.addEventListener("change", loadProducts);

  // Initial load
  await loadProducts();
}
