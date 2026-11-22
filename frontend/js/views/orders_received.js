import { ordersApi, getCurrentUser, escapeHtml } from "../api.js";
import { showToast, confirmDialog } from "../app.js";

export async function renderOrdersReceivedView(container) {
  const user = getCurrentUser();
  const isAdmin = user && user.role === "admin";

  container.innerHTML = `
    <div class="section-header">
      <div>
        <h2 class="section-title">${isAdmin ? "All Platform Orders" : "Orders Received"}</h2>
        <p class="section-subtitle">Fulfill customer orders, advance dispatch status, and manage shipments.</p>
      </div>
    </div>

    <div id="receivedOrdersArea">
      <div class="empty-state">
        <p>Loading incoming orders...</p>
      </div>
    </div>
  `;

  const receivedOrdersArea = document.getElementById("receivedOrdersArea");

  async function loadReceivedOrders() {
    receivedOrdersArea.innerHTML = `<div class="empty-state"><p>Loading orders...</p></div>`;
    try {
      const orders = await ordersApi.getReceivedOrders();

      if (!orders || orders.length === 0) {
        receivedOrdersArea.innerHTML = `
          <div class="empty-state">
            <div class="empty-state-icon">📑</div>
            <h3>No incoming orders yet</h3>
            <p>When customers purchase your listed plant specimens, they will appear here for processing.</p>
          </div>
        `;
        return;
      }

      const statusBadges = {
        "pending": "background: #fff8e1; color: #b7791f; border: 1px solid #ffe082;",
        "confirmed": "background: #e3f2fd; color: #1565c0; border: 1px solid #90caf9;",
        "shipped": "background: #f3e5f5; color: #7b1fa2; border: 1px solid #ce93d8;",
        "delivered": "background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7;",
        "cancelled": "background: #ffebee; color: #c62828; border: 1px solid #ffcdd2;",
      };

      const NEXT_STATUS = {
        "pending": { next: "confirmed", label: "Confirm Order" },
        "confirmed": { next: "shipped", label: "Ship Order (Dispatched)" },
        "shipped": { next: "delivered", label: "Mark Delivered" },
      };

      receivedOrdersArea.innerHTML = orders.map(order => {
        const dateStr = new Date(order.created_at).toLocaleDateString("en-US", {
          year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
        });

        const nextAction = NEXT_STATUS[order.status];

        const itemsHtml = order.items.map(i => `
          <div style="display: flex; justify-content: space-between; padding: 0.4rem 0; border-bottom: 1px dashed var(--border); font-size: 0.88rem;">
            <span><strong>${escapeHtml(i.product_name)}</strong> &times; ${i.quantity}</span>
            <span>NPR ${i.subtotal.toLocaleString()}</span>
          </div>
        `).join("");

        return `
          <div class="order-card" style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem;">
              <div>
                <span class="badge" style="${statusBadges[order.status] || ''}; margin-bottom: 0.35rem;">
                  ${order.status.toUpperCase()}
                </span>
                <h3 style="font-family: var(--font-serif); font-size: 1.25rem; color: var(--primary-dark); margin: 0.2rem 0;">
                  #RR-${order.id} &bull; Customer: ${escapeHtml(order.buyer_name || 'Buyer')}
                </h3>
                <div style="font-size: 0.82rem; color: var(--text-muted);">
                  ${dateStr} &bull; Email: ${escapeHtml(order.buyer_email || 'N/A')}
                </div>
              </div>

              <!-- Action button to advance status -->
              <div>
                ${nextAction ? `
                  <button class="btn btn-primary btn-sm advance-status-btn" data-id="${order.id}" data-next="${nextAction.next}" data-label="${nextAction.label}">
                    ${nextAction.label} &rarr;
                  </button>
                ` : `
                  <span style="font-size: 0.82rem; color: var(--text-muted); font-weight: 600;">
                    ${order.status === 'delivered' ? '✓ Completed' : '✕ Cancelled'}
                  </span>
                `}
              </div>
            </div>

            <!-- Items -->
            <div style="background: var(--bg-main); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 0.9rem 1.1rem; margin-bottom: 1rem;">
              <div style="font-size: 0.78rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700; margin-bottom: 0.4rem;">
                ${isAdmin ? "Order Items" : "Your Products in this Order"}
              </div>
              ${itemsHtml}
              <div style="display: flex; justify-content: space-between; font-weight: 700; font-size: 1.05rem; color: var(--primary); margin-top: 0.6rem; padding-top: 0.5rem; border-top: 1px solid var(--border);">
                <span>Subtotal</span>
                <span>NPR ${order.total.toLocaleString()}</span>
              </div>
            </div>

            <div style="font-size: 0.85rem; color: var(--text-muted); display: flex; gap: 2rem; flex-wrap: wrap;">
              <div>📍 Delivery Address: <strong>${escapeHtml(order.shipping_address)}</strong></div>
              <div>🌍 Country: <strong>${escapeHtml(order.destination_country)}</strong></div>
            </div>
          </div>
        `;
      }).join("");

      // Bind advance status buttons
      receivedOrdersArea.querySelectorAll(".advance-status-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const orderId = btn.dataset.id;
          const targetStatus = btn.dataset.next;
          const label = btn.dataset.label;

          confirmDialog(
            `${label}?`,
            `Are you sure you want to update the status of order #RR-${orderId} to "${targetStatus}"?`,
            async () => {
              try {
                await ordersApi.updateStatus(orderId, targetStatus);
                showToast(`Order status updated to ${targetStatus}!`, "success");
                await loadReceivedOrders();
              } catch (err) {
                showToast(err.message, "error");
              }
            }
          );
        });
      });

    } catch (err) {
      receivedOrdersArea.innerHTML = `
        <div class="empty-state">
          <p style="color: var(--danger);">Failed to load orders: ${escapeHtml(err.message)}</p>
        </div>
      `;
    }
  }

  await loadReceivedOrders();
}
