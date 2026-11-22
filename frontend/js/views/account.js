import { usersApi, authApi, getCurrentUser, setCurrentUser, clearAuth, escapeHtml } from "../api.js";
import { showToast } from "../app.js";

export async function renderAccountView(container) {
  const user = getCurrentUser();

  const dateStr = user && user.created_at ? new Date(user.created_at).toLocaleDateString("en-US", {
    year: "numeric", month: "long", day: "numeric"
  }) : "Recent";

  container.innerHTML = `
    <div class="section-header">
      <div>
        <h2 class="section-title">Account Settings</h2>
        <p class="section-subtitle">Manage your profile information and security credentials.</p>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">
      
      <!-- Profile Information Card -->
      <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 2rem; box-shadow: var(--shadow-sm);">
        <h3 class="font-serif" style="font-size: 1.35rem; margin-bottom: 0.5rem;">Profile Information</h3>
        <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 1.5rem;">
          Update your public botanical display name.
        </p>

        <form id="updateProfileForm">
          <div class="form-group">
            <label for="accEmail">Email Address (Read-only)</label>
            <input type="email" id="accEmail" class="form-input" value="${escapeHtml(user ? user.email : '')}" disabled style="background: var(--bg-main); color: var(--text-muted);">
            <div class="form-hint">Email address is your unique system identifier.</div>
          </div>

          <div class="form-group">
            <label for="accRole">Account Role</label>
            <input type="text" id="accRole" class="form-input" value="${escapeHtml(user ? user.role.toUpperCase() : '')}" disabled style="background: var(--bg-main); color: var(--text-muted); font-weight: 700;">
          </div>

          <div class="form-group">
            <label for="accName">Full Name / Nursery Name</label>
            <input type="text" id="accName" class="form-input" value="${escapeHtml(user ? user.full_name : '')}" required minlength="2">
          </div>

          <button type="submit" class="btn btn-primary" id="saveProfileBtn">
            Save Changes
          </button>
        </form>
      </div>

      <!-- Security & Password Card -->
      <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 2rem; box-shadow: var(--shadow-sm);">
        <h3 class="font-serif" style="font-size: 1.35rem; margin-bottom: 0.5rem;">Security Credentials</h3>
        <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 1.5rem;">
          Changing your password will terminate your current session and require re-authentication.
        </p>

        <form id="changePasswordForm">
          <div class="form-group">
            <label for="currentPassword">Current Password</label>
            <input type="password" id="currentPassword" class="form-input" placeholder="••••••••" required>
          </div>

          <div class="form-group">
            <label for="newPassword">New Password</label>
            <input type="password" id="newPassword" class="form-input" placeholder="8-64 chars, letter & number" required minlength="8">
            <div class="form-hint">Must contain at least 8 characters, one letter, and one number.</div>
          </div>

          <div class="form-group">
            <label for="confirmNewPassword">Confirm New Password</label>
            <input type="password" id="confirmNewPassword" class="form-input" placeholder="••••••••" required minlength="8">
          </div>

          <button type="submit" class="btn btn-accent" id="changePasswordBtn">
            Update Password & Sign Out
          </button>
        </form>
      </div>

    </div>
  `;

  // Profile form submit
  const profileForm = document.getElementById("updateProfileForm");
  profileForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const newName = document.getElementById("accName").value.trim();
    const saveBtn = document.getElementById("saveProfileBtn");

    saveBtn.disabled = true;
    saveBtn.textContent = "Saving...";

    try {
      const updated = await usersApi.updateMe({ full_name: newName });
      setCurrentUser(updated);
      showToast("Profile name updated successfully!", "success");
      const nameElem = document.getElementById("headerUserName");
      if (nameElem) nameElem.textContent = updated.full_name;
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      saveBtn.disabled = false;
      saveBtn.textContent = "Save Changes";
    }
  });

  // Password form submit
  const passwordForm = document.getElementById("changePasswordForm");
  passwordForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const currentPass = document.getElementById("currentPassword").value;
    const newPass = document.getElementById("newPassword").value;
    const confirmPass = document.getElementById("confirmNewPassword").value;
    const changeBtn = document.getElementById("changePasswordBtn");

    if (newPass !== confirmPass) {
      showToast("New passwords do not match.", "error");
      return;
    }

    changeBtn.disabled = true;
    changeBtn.textContent = "Updating Password...";

    try {
      await authApi.changePassword({
        current_password: currentPass,
        new_password: newPass
      });
      showToast("Password updated successfully! Session ended.", "success");
      clearAuth();
      setTimeout(() => {
        window.location.href = "index.html";
      }, 1200);
    } catch (err) {
      showToast(err.message, "error");
      changeBtn.disabled = false;
      changeBtn.textContent = "Update Password & Sign Out";
    }
  });
}
