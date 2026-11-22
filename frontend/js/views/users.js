import { usersApi, getCurrentUser, escapeHtml } from "../api.js";
import { showToast, confirmDialog } from "../app.js";

export async function renderUsersView(container) {
  const currentUser = getCurrentUser();

  container.innerHTML = `
    <div class="section-header">
      <div>
        <h2 class="section-title">User Accounts Administration</h2>
        <p class="section-subtitle">Manage user roles, review seller approval requests, and handle account activation.</p>
      </div>
    </div>

    <div class="table-container" id="usersTableArea">
      <div class="empty-state">
        <p>Loading user accounts...</p>
      </div>
    </div>
  `;

  const usersTableArea = document.getElementById("usersTableArea");

  async function loadUsers() {
    usersTableArea.innerHTML = `<div class="empty-state"><p>Loading accounts...</p></div>`;
    try {
      const users = await usersApi.listUsers();

      const rowsHtml = users.map(u => {
        const isSelf = currentUser && u.id === currentUser.id;
        const dateStr = new Date(u.created_at).toLocaleDateString("en-US", {
          year: "numeric", month: "short", day: "numeric"
        });

        return `
          <tr data-id="${u.id}">
            <td style="font-weight: 600; color: var(--text-muted);">#${u.id}</td>
            <td>
              <strong style="color: var(--primary-dark); font-size: 0.95rem;">${escapeHtml(u.full_name)}</strong>
              ${isSelf ? '<span class="badge" style="background:#e0f2fe; color:#0369a1; margin-left: 0.35rem;">You</span>' : ''}
              <div style="font-size: 0.8rem; color: var(--text-muted);">${escapeHtml(u.email)}</div>
            </td>
            <td>
              ${isSelf ? `
                <span class="role-tag ${u.role}">${u.role.toUpperCase()}</span>
              ` : `
                <select class="form-select user-role-select" data-id="${u.id}" style="padding: 0.25rem 0.6rem; font-size: 0.82rem; width: 110px;">
                  <option value="buyer" ${u.role === 'buyer' ? 'selected' : ''}>Buyer</option>
                  <option value="seller" ${u.role === 'seller' ? 'selected' : ''}>Seller</option>
                  <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>Admin</option>
                </select>
              `}
            </td>
            <td>
              ${u.role === 'seller' ? `
                <button class="btn btn-sm ${u.is_approved ? 'btn-outline' : 'btn-accent'} toggle-approve-btn" data-id="${u.id}" data-approved="${u.is_approved}" style="font-size: 0.75rem; padding: 0.2rem 0.6rem;">
                  ${u.is_approved ? '✓ Approved' : '⏳ Pending Review'}
                </button>
              ` : `
                <span style="font-size: 0.8rem; color: var(--text-light);">Auto-approved</span>
              `}
            </td>
            <td>
              ${isSelf ? `
                <span class="badge" style="background: var(--success-bg); color: var(--success);">Active</span>
              ` : `
                <button class="btn btn-sm ${u.is_active ? 'btn-outline' : 'btn-danger'} toggle-status-btn" data-id="${u.id}" data-active="${u.is_active}" style="font-size: 0.75rem; padding: 0.2rem 0.6rem;">
                  ${u.is_active ? 'Active' : 'Deactivated'}
                </button>
              `}
            </td>
            <td style="font-size: 0.82rem; color: var(--text-muted);">${dateStr}</td>
          </tr>
        `;
      }).join("");

      usersTableArea.innerHTML = `
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>User</th>
              <th>Role</th>
              <th>Seller Approval</th>
              <th>Account Status</th>
              <th>Registered</th>
            </tr>
          </thead>
          <tbody>
            ${rowsHtml}
          </tbody>
        </table>
      `;

      // Bind role change
      usersTableArea.querySelectorAll(".user-role-select").forEach(sel => {
        sel.addEventListener("change", async () => {
          const userId = sel.dataset.id;
          const newRole = sel.value;
          try {
            await usersApi.updateRole(userId, newRole);
            showToast(`User role updated to ${newRole}!`, "success");
            await loadUsers();
          } catch (err) {
            showToast(err.message, "error");
            await loadUsers();
          }
        });
      });

      // Bind seller approval toggle
      usersTableArea.querySelectorAll(".toggle-approve-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
          const userId = btn.dataset.id;
          const currentlyApproved = btn.dataset.approved === "true";
          const newStatus = !currentlyApproved;
          try {
            await usersApi.approveSeller(userId, newStatus);
            showToast(`Seller status changed to ${newStatus ? 'Approved' : 'Pending'}!`, "success");
            await loadUsers();
          } catch (err) {
            showToast(err.message, "error");
          }
        });
      });

      // Bind active status toggle
      usersTableArea.querySelectorAll(".toggle-status-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const userId = btn.dataset.id;
          const currentlyActive = btn.dataset.active === "true";
          const newStatus = !currentlyActive;

          confirmDialog(
            `${newStatus ? 'Activate' : 'Deactivate'} User Account?`,
            `Are you sure you want to ${newStatus ? 'reactivate' : 'deactivate'} this user account? Deactivated accounts cannot sign in.`,
            async () => {
              try {
                await usersApi.updateStatus(userId, newStatus);
                showToast(`Account ${newStatus ? 'reactivated' : 'deactivated'} successfully!`, "info");
                await loadUsers();
              } catch (err) {
                showToast(err.message, "error");
              }
            }
          );
        });
      });

    } catch (err) {
      usersTableArea.innerHTML = `
        <div class="empty-state">
          <p style="color: var(--danger);">Failed to load users: ${escapeHtml(err.message)}</p>
        </div>
      `;
    }
  }

  await loadUsers();
}
