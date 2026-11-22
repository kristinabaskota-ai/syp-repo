import { cartApi, ordersApi, escapeHtml } from "../api.js";
import { openModal, closeModal, showToast, updateCartBadge } from "../app.js";

export async function renderCartView(container) {
  container.innerHTML = `
    <div class="section-header">
      <div>
        <h2 class="section-title">Your Cart</h2>
        <p class="section-subtitle">Review selected botanical specimens before secure transactional checkout.</p>
      </div>
      <div id="cartHeaderActions" style="display: none;">
        <button class="btn btn-secondary btn-sm" id="clearCartBtn">Clear Entire Cart</button>
      </div>
    </div>

    <div id="cartContentArea">
      <div class="empty-state">
        <p>Loading your shopping cart...</p>
      </div>
    </div>
  `;

  const cartContentArea = document.getElementById("cartContentArea");
  const cartHeaderActions = document.getElementById("cartHeaderActions");
  const clearCartBtn = document.getElementById("clearCartBtn");

  async function loadCart() {
    try {
      const cart = await cartApi.getCart();
      await updateCartBadge();

      if (!cart.items || cart.items.length === 0) {
        cartHeaderActions.style.display = "none";
        cartContentArea.innerHTML = `
          <div class="empty-state">
            <div class="empty-state-icon">🛒</div>
            <h3>Your cart is empty</h3>
            <p>Explore our rare botanical collection and add plants to your cart.</p>
            <a href="#shop" class="btn btn-primary">Browse Plant Shop</a>
          </div>
        `;
        return;
      }

      cartHeaderActions.style.display = "block";

      const fallbackImg = "https://images.unsplash.com/photo-1545241047-6083a3684587?w=600&auto=format&fit=crop&q=80";

      const itemsHtml = cart.items.map(item => {
        const p = item.product;
        return `
          <div class="cart-item-card" data-item-id="${item.id}" style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.25rem; display: flex; align-items: center; justify-content: space-between; gap: 1.25rem; margin-bottom: 1rem; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 1rem; flex: 1; min-width: 240px;">
              <img src="${escapeHtml(p.image_url || fallbackImg)}" alt="${escapeHtml(p.name)}" style="width: 70px; height: 70px; border-radius: var(--radius-sm); object-fit: cover;" onerror="this.src='${fallbackImg}'">
              <div>
                <h4 style="font-size: 1.05rem; margin-bottom: 0.2rem; font-family: var(--font-serif);">${escapeHtml(p.name)}</h4>
                <div style="font-size: 0.82rem; color: var(--text-muted);">
                  Unit Price: NPR ${p.price.toLocaleString()} &bull; Stock Available: ${p.stock}
                </div>
              </div>
            </div>

            <div style="display: flex; align-items: center; gap: 1.5rem;">
              <div style="display: flex; align-items: center; border: 1px solid var(--border); border-radius: var(--radius-sm); overflow: hidden;">
                <button class="btn btn-secondary btn-sm qty-dec-btn" style="border-radius: 0; padding: 0.4rem 0.75rem;" data-id="${item.id}" data-current="${item.quantity}">-</button>
                <span style="min-width: 40px; text-align: center; font-weight: 600; font-size: 0.9rem;">${item.quantity}</span>
                <button class="btn btn-secondary btn-sm qty-inc-btn" style="border-radius: 0; padding: 0.4rem 0.75rem;" data-id="${item.id}" data-current="${item.quantity}" data-max="${p.stock}">+</button>
              </div>

              <div style="min-width: 110px; text-align: right;">
                <div style="font-weight: 700; font-size: 1.1rem; color: var(--primary);">
                  <span style="font-size: 0.8rem; font-weight: 500;">NPR</span> ${item.item_total.toLocaleString()}
                </div>
              </div>

              <button class="btn btn-secondary btn-sm cart-remove-btn" data-id="${item.id}" title="Remove Item" style="color: var(--danger);">
                🗑️
              </button>
            </div>
          </div>
        `;
      }).join("");

      cartContentArea.innerHTML = `
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; align-items: start;">
          <div>
            ${itemsHtml}
          </div>
          <!-- Order Summary Card -->
          <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.5rem; position: sticky; top: 90px; box-shadow: var(--shadow-sm);">
            <h3 style="font-size: 1.25rem; font-family: var(--font-serif); margin-bottom: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: 0.75rem;">
              Order Summary
            </h3>
            <div style="display: flex; justify-content: space-between; font-size: 0.95rem; margin-bottom: 0.75rem; color: var(--text-muted);">
              <span>Items Total (${cart.items.length} species)</span>
              <span>NPR ${cart.total.toLocaleString()}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.95rem; margin-bottom: 0.75rem; color: var(--text-muted);">
              <span>Estimated Shipping</span>
              <span style="color: var(--success); font-weight: 600;">Complimentary</span>
            </div>
            <div style="border-top: 2px dashed var(--border); margin: 1rem 0; padding-top: 1rem; display: flex; justify-content: space-between; font-size: 1.3rem; font-weight: 700; color: var(--primary);">
              <span>Total</span>
              <span>NPR ${cart.total.toLocaleString()}</span>
            </div>
            <button class="btn btn-primary btn-block" id="proceedCheckoutBtn" style="padding: 0.85rem;">
              Proceed to Checkout
            </button>
            <div style="font-size: 0.78rem; color: var(--text-muted); text-align: center; margin-top: 0.85rem;">
              🔒 Stock is validated and deducted atomically upon checkout.
            </div>
          </div>
        </div>
      `;

      // Bind quantity decrease
      cartContentArea.querySelectorAll(".qty-dec-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
          const current = parseInt(btn.dataset.current);
          const itemId = btn.dataset.id;
          if (current <= 1) {
            // Remove item
            await cartApi.removeItem(itemId);
            showToast("Item removed from cart", "info");
          } else {
            await cartApi.updateQuantity(itemId, current - 1);
          }
          await loadCart();
        });
      });

      // Bind quantity increase
      cartContentArea.querySelectorAll(".qty-inc-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
          const current = parseInt(btn.dataset.current);
          const max = parseInt(btn.dataset.max);
          const itemId = btn.dataset.id;
          if (current >= max) {
            showToast(`Cannot add more. Maximum available stock is ${max}.`, "error");
            return;
          }
          try {
            await cartApi.updateQuantity(itemId, current + 1);
            await loadCart();
          } catch (err) {
            showToast(err.message, "error");
          }
        });
      });

      // Bind remove button
      cartContentArea.querySelectorAll(".cart-remove-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
          const itemId = btn.dataset.id;
          try {
            await cartApi.removeItem(itemId);
            showToast("Item removed from cart", "info");
            await loadCart();
          } catch (err) {
            showToast(err.message, "error");
          }
        });
      });

      // Bind checkout button
      document.getElementById("proceedCheckoutBtn").addEventListener("click", () => {
        showCartCheckoutModal(cart);
      });

    } catch (err) {
      cartContentArea.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">⚠️</div>
          <h3>Failed to load cart</h3>
          <p>${escapeHtml(err.message)}</p>
        </div>
      `;
    }
  }

  function showCartCheckoutModal(cart) {
    openModal(`
      <div class="modal-header">
        <h3 class="modal-title font-serif">Checkout Order</h3>
        <button class="modal-close-btn" data-close-modal>&times;</button>
      </div>
      <form id="cartCheckoutForm">
        <div class="modal-body">
          <div style="background: var(--bg-main); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 1.25rem;">
            <div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.4rem;">
              Total Order Value (${cart.items.length} items):
            </div>
            <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary);">
              NPR ${cart.total.toLocaleString()}
            </div>
          </div>

          <div class="form-group">
            <label for="checkoutAddress">Shipping & Delivery Address</label>
            <input type="text" id="checkoutAddress" class="form-input" placeholder="e.g. Ward 3, Jhamsikhel, Lalitpur" required minlength="5">
            <div class="form-hint">Please provide detailed door/street information for plant courier delivery.</div>
          </div>

          <div class="form-group">
            <label for="checkoutCountry">Destination Country</label>
            <input type="text" id="checkoutCountry" class="form-input" value="Nepal" required>
            <div class="form-hint">Default delivery country is Nepal. Ensure destination import rules are satisfied.</div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-close-modal>Cancel</button>
          <button type="submit" class="btn btn-primary" id="confirmCheckoutBtn">
            Confirm & Complete Order
          </button>
        </div>
      </form>
    `);

    document.getElementById("cartCheckoutForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const address = document.getElementById("checkoutAddress").value.trim();
      const country = document.getElementById("checkoutCountry").value.trim();
      const submitBtn = document.getElementById("confirmCheckoutBtn");

      submitBtn.disabled = true;
      submitBtn.textContent = "Processing Checkout...";

      try {
        const order = await ordersApi.checkout({
          shipping_address: address,
          destination_country: country,
        });
        closeModal();
        showToast("Order placed successfully! Inventory updated.", "success");
        await updateCartBadge();
        window.location.hash = "#orders";
      } catch (err) {
        showToast(err.message, "error");
        submitBtn.disabled = false;
        submitBtn.textContent = "Confirm & Complete Order";
      }
    });
  }

  // Clear cart button
  clearCartBtn.addEventListener("click", async () => {
    try {
      await cartApi.clearCart();
      showToast("Cart has been cleared", "info");
      await loadCart();
    } catch (err) {
      showToast(err.message, "error");
    }
  });

  await loadCart();
}
