import { reportsApi, escapeHtml } from "../api.js";

export async function renderReportsView(container) {
  container.innerHTML = `
    <div class="section-header">
      <div>
        <h2 class="section-title">Platform Reports & Analytics</h2>
        <p class="section-subtitle">Real-time marketplace telemetry, transaction volume, and epidemiological diagnostic patterns.</p>
      </div>
      <div>
        <button class="btn btn-secondary btn-sm" id="refreshReportsBtn">↻ Refresh Analytics</button>
      </div>
    </div>

    <div id="reportsContentArea">
      <div class="empty-state">
        <p>Compiling analytics telemetry...</p>
      </div>
    </div>
  `;

  const reportsContentArea = document.getElementById("reportsContentArea");
  const refreshReportsBtn = document.getElementById("refreshReportsBtn");

  async function loadReports() {
    reportsContentArea.innerHTML = `<div class="empty-state"><p>Compiling analytics telemetry...</p></div>`;
    try {
      const data = await reportsApi.getReports();

      const totalUsers = Object.values(data.users_by_role).reduce((a, b) => a + b, 0);
      const totalOrders = Object.values(data.orders_by_status).reduce((a, b) => a + b, 0);

      // Top products table rows
      const topProductsRows = data.top_products.length === 0 ? `
        <tr><td colspan="3" style="text-align: center; color: var(--text-muted);">No sales recorded yet.</td></tr>
      ` : data.top_products.map((p, idx) => `
        <tr>
          <td><strong style="color: var(--primary);">#${idx + 1}</strong> ${escapeHtml(p.product_name)}</td>
          <td>${p.total_quantity_sold} units</td>
          <td style="font-weight: 700;">NPR ${p.total_revenue.toLocaleString()}</td>
        </tr>
      `).join("");

      // Common diagnoses table rows
      const diagnosesRows = data.common_diagnoses.length === 0 ? `
        <tr><td colspan="3" style="text-align: center; color: var(--text-muted);">No diagnostic logs recorded yet.</td></tr>
      ` : data.common_diagnoses.map((d, idx) => `
        <tr>
          <td><span style="font-weight: 700; color: var(--primary);">#${idx + 1}</span> ${escapeHtml(d.diagnosis)}</td>
          <td><span class="badge" style="background:#e8f5e9; color:#2e7d32; text-transform: capitalize;">${escapeHtml(d.plant_part)}</span></td>
          <td><strong>${d.count}</strong> consults</td>
        </tr>
      `).join("");

      // Low stock list
      const lowStockRows = data.low_stock_products.length === 0 ? `
        <p style="color: var(--success); font-weight: 600; font-size: 0.9rem;">✓ All products are healthy above threshold.</p>
      ` : data.low_stock_products.map(p => `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0; border-bottom: 1px dashed var(--border); font-size: 0.88rem;">
          <div>
            <strong>${escapeHtml(p.name)}</strong>
            <span style="color: var(--text-muted); font-size: 0.8rem; margin-left: 0.4rem;">(${escapeHtml(p.category_name || 'Plant')})</span>
          </div>
          <div>
            <span class="badge" style="${p.stock === 0 ? 'background:#ffebee; color:#c62828;' : 'background:#fff8e1; color:#b7791f;'} font-weight: 700;">
              ${p.stock === 0 ? 'Sold Out (0)' : `${p.stock} left`}
            </span>
          </div>
        </div>
      `).join("");

      reportsContentArea.innerHTML = `
        <!-- High-level KPI Metric Cards -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem; margin-bottom: 2rem;">
          <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.5rem; box-shadow: var(--shadow-sm);">
            <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Total Sales (Valid Orders)</div>
            <div style="font-size: 1.9rem; font-weight: 800; color: var(--primary); margin: 0.35rem 0;">
              <span style="font-size: 1rem; font-weight: 600;">NPR</span> ${data.total_sales.toLocaleString()}
            </div>
            <div style="font-size: 0.78rem; color: var(--text-light);">Excludes cancelled orders</div>
          </div>

          <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.5rem; box-shadow: var(--shadow-sm);">
            <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Total Orders Placed</div>
            <div style="font-size: 1.9rem; font-weight: 800; color: var(--primary-dark); margin: 0.35rem 0;">
              ${totalOrders}
            </div>
            <div style="font-size: 0.78rem; color: var(--text-light);">${data.orders_by_status.pending || 0} currently pending</div>
          </div>

          <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.5rem; box-shadow: var(--shadow-sm);">
            <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Registered Users</div>
            <div style="font-size: 1.9rem; font-weight: 800; color: var(--primary-dark); margin: 0.35rem 0;">
              ${totalUsers}
            </div>
            <div style="font-size: 0.78rem; color: var(--text-light);">${data.users_by_role.seller || 0} nurseries &bull; ${data.users_by_role.buyer || 0} buyers</div>
          </div>

          <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.5rem; box-shadow: var(--shadow-sm);">
            <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Low Stock Alerts (&le; 5)</div>
            <div style="font-size: 1.9rem; font-weight: 800; color: ${data.low_stock_count > 0 ? 'var(--warning)' : 'var(--success)'}; margin: 0.35rem 0;">
              ${data.low_stock_count}
            </div>
            <div style="font-size: 0.78rem; color: var(--text-light);">Inventory restock needed</div>
          </div>
        </div>

        <!-- Breakdown Grid -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem;">
          <!-- Orders by Status -->
          <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.5rem; box-shadow: var(--shadow-sm);">
            <h3 class="font-serif" style="font-size: 1.25rem; margin-bottom: 1rem;">Orders by Status</h3>
            <div style="display: flex; flex-direction: column; gap: 0.65rem;">
              <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                <span>⏳ Pending</span>
                <strong>${data.orders_by_status.pending || 0}</strong>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                <span>🔍 Confirmed</span>
                <strong>${data.orders_by_status.confirmed || 0}</strong>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                <span>🚚 Shipped</span>
                <strong>${data.orders_by_status.shipped || 0}</strong>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                <span>✅ Delivered</span>
                <strong>${data.orders_by_status.delivered || 0}</strong>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 0.9rem; color: var(--danger);">
                <span>✕ Cancelled</span>
                <strong>${data.orders_by_status.cancelled || 0}</strong>
              </div>
            </div>
          </div>

          <!-- User Role Distribution -->
          <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.5rem; box-shadow: var(--shadow-sm);">
            <h3 class="font-serif" style="font-size: 1.25rem; margin-bottom: 1rem;">User Community Breakdown</h3>
            <div style="display: flex; flex-direction: column; gap: 0.65rem;">
              <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                <span>🛒 Plant Collectors (Buyers)</span>
                <strong>${data.users_by_role.buyer || 0}</strong>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                <span>🏡 Nurseries (Sellers)</span>
                <strong>${data.users_by_role.seller || 0}</strong>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                <span>🛡️ Platform Administrators</span>
                <strong>${data.users_by_role.admin || 0}</strong>
              </div>
            </div>
          </div>
        </div>

        <!-- Tables Row -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem;">
          <!-- Top Selling Products -->
          <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.5rem; box-shadow: var(--shadow-sm);">
            <h3 class="font-serif" style="font-size: 1.25rem; margin-bottom: 1rem;">Top Selling Plant Specimens</h3>
            <table class="data-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Quantity</th>
                  <th>Revenue</th>
                </tr>
              </thead>
              <tbody>
                ${topProductsRows}
              </tbody>
            </table>
          </div>

          <!-- Most Common Diagnoses -->
          <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.5rem; box-shadow: var(--shadow-sm);">
            <h3 class="font-serif" style="font-size: 1.25rem; margin-bottom: 1rem;">Frequent Plant Health Diagnoses</h3>
            <table class="data-table">
              <thead>
                <tr>
                  <th>Condition</th>
                  <th>Part</th>
                  <th>Frequency</th>
                </tr>
              </thead>
              <tbody>
                ${diagnosesRows}
              </tbody>
            </table>
          </div>
        </div>

        <!-- Low Stock Alert Box -->
        <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.5rem; box-shadow: var(--shadow-sm);">
          <h3 class="font-serif" style="font-size: 1.25rem; margin-bottom: 0.5rem;">Inventory Depletion Alert</h3>
          <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 1rem;">Specimens with 5 or fewer units remaining in nursery stocks.</p>
          <div>
            ${lowStockRows}
          </div>
        </div>
      `;

    } catch (err) {
      reportsContentArea.innerHTML = `
        <div class="empty-state">
          <p style="color: var(--danger);">Failed to load analytics: ${escapeHtml(err.message)}</p>
        </div>
      `;
    }
  }

  refreshReportsBtn.addEventListener("click", loadReports);
  await loadReports();
}
