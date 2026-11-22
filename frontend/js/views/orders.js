import { ordersApi, escapeHtml } from "../api.js";
import { showToast, confirmDialog } from "../app.js";

export async function renderOrdersView(container) {
  container.innerHTML = `
    <div class="section-header">
      <div>
        <h2 class="section-title">My Orders</h2>
        <p class="section-subtitle">Track fulfillment status, courier dispatch, and purchase history.</p>
      </div>
    </div>

    <div id="ordersListArea">
      <div class="empty-state">
        <p>Loading your orders...</p>
      </div>
    </div>
  `;

  const ordersListArea = document.getElementById("ordersListArea");

  async function loadOrders() {
    try {
      const orders = await ordersApi.getMyOrders();

      if (!orders || orders.length === 0) {
        ordersListArea.innerHTML = `
          <div class="empty-state">
            <div class="empty-state-icon">📦</div>
            <h3>No orders yet</h3>
            <p>You haven't placed any orders yet. Visit our shop to find rare botanical specimens.</p>
            <a href="#shop" class="btn btn-primary">Start Shopping</a>
          </div>
        `;
        return;
      }

      ordersListArea.innerHTML = orders.map(order => {
        const dateStr = new Date(order.created_at).toLocaleDateString("en-US", {
          year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
        });

        const statusColors = {
          "pending": "background: #fff8e1; color: #b7791f; border: 1px solid #ffe082;",
          "confirmed": "background: #e3f2fd; color: #1565c0; border: 1px solid #90caf9;",
          "shipped": "background: #f3e5f5; color: #7b1fa2; border: 1px solid #ce93d8;",
          "delivered": "background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7;",
          "cancelled": "background: #ffebee; color: #c62828; border: 1px solid #ffcdd2;",
        };

        const statusStyle = statusColors[order.status] || "background: #eee; color: #333;";
        const isPending = order.status === "pending";

        const itemsHtml = order.items.map(item => `
          <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0; border-bottom: 1px dashed var(--border); font-size: 0.9rem;">
            <div>
              <strong>${escapeHtml(item.product_name)}</strong>
              <span style="color: var(--text-muted); font-size: 0.82rem; margin-left: 0.5rem;">&times; ${item.quantity}</span>
            </div>
            <div style="font-weight: 600;">
              NPR ${item.subtotal.toLocaleString()}
            </div>
          </div>
        `).join("");

        return `
          <div class="order-card" style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 0.75rem;">
              <div>
                <div style="font-size: 0.82rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em;">Order Reference</div>
                <h3 style="font-family: var(--font-serif); font-size: 1.25rem; color: var(--primary-dark);">#RR-${order.id}</h3>
                <div style="font-size: 0.82rem; color: var(--text-light);">${dateStr}</div>
              </div>

              <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span class="badge" style="${statusStyle}; padding: 0.35rem 0.85rem; font-size: 0.82rem;">
                  ${order.status.toUpperCase()}
                </span>
                ${isPending ? `
                  <button class="btn btn-secondary btn-sm cancel-order-btn" data-id="${order.id}" style="color: var(--danger); border-color: #ffcdd2;">
                    Cancel Order
                  </button>
                ` : ""}
              </div>
            </div>

            <!-- Items -->
            <div style="background: var(--bg-main); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 1rem 1.25rem; margin-bottom: 1.25rem;">
              ${itemsHtml}
              <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 0.75rem; font-size: 1.15rem; font-weight: 700; color: var(--primary);">
                <span>Total Amount Paid</span>
                <span>NPR ${order.total.toLocaleString()}</span>
              </div>
            </div>

            <div style="font-size: 0.85rem; color: var(--text-muted); display: flex; gap: 2rem; flex-wrap: wrap;">
              <div>📍 Delivery Address: <strong>${escapeHtml(order.shipping_address)}</strong></div>
              <div>🌍 Destination: <strong>${escapeHtml(order.destination_country)}</strong></div>
            </div>
          </div>
        `;
      }).join("");

      // Bind cancel buttons
      ordersListArea.querySelectorAll(".cancel-order-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const orderId = btn.dataset.id;
          confirmDialog(
            "Cancel Order?",
            `Are you sure you want to cancel order #RR-${orderId}? The reserved botanical inventory will be returned to the store stock immediately.`,
            async () => {
              try {
                await ordersApi.cancelOrder(orderId);
                showToast("Order cancelled and stock restored to store inventory.", "success");
                await loadOrders();
              } catch (err) {
                showToast(err.message, "error");
              }
            }
          );
        });
      });

    } catch (err) {
      ordersListArea.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">⚠️</div>
          <h3>Failed to load orders</h3>
          <p>${escapeHtml(err.message)}</p>
        </div>
      `;
    }
  }

  await loadOrders();
}
