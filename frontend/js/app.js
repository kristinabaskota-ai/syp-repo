/**
 * RareRoot App Controller
 * Hash-based router, state management, modal & toast services.
 */
import {
  getToken, getCurrentUser, setCurrentUser, clearAuth,
  authApi, usersApi, cartApi
} from "./api.js";

// View modules
import { renderShopView } from "./views/shop.js";
import { renderCartView } from "./views/cart.js";
import { renderOrdersView } from "./views/orders.js";
import { renderDoctorView } from "./views/doctor.js";
import { renderWantedView } from "./views/wanted.js";
import { renderImportCheckView } from "./views/import_check.js";
import { renderListingsView } from "./views/listings.js";
import { renderOrdersReceivedView } from "./views/orders_received.js";
import { renderUsersView } from "./views/users.js";
import { renderImportRulesView } from "./views/import_rules.js";
import { renderReportsView } from "./views/reports.js";
import { renderAccountView } from "./views/account.js";

// Route registry
const ROUTES = {
  "shop": renderShopView,
  "cart": renderCartView,
  "orders": renderOrdersView,
  "doctor": renderDoctorView,
  "wanted": renderWantedView,
  "import-check": renderImportCheckView,
  "listings": renderListingsView,
  "orders-received": renderOrdersReceivedView,
  "users": renderUsersView,
  "import-rules": renderImportRulesView,
  "reports": renderReportsView,
  "account": renderAccountView,
};

// UI Elements
const mainContent = document.getElementById("mainContent");
const toastContainer = document.getElementById("toastContainer");
const modalOverlay = document.getElementById("globalModalOverlay");
const modalContent = document.getElementById("globalModalContent");
const headerUserName = document.getElementById("headerUserName");
const headerUserAvatar = document.getElementById("headerUserAvatar");
const headerUserRole = document.getElementById("headerUserRole");
const headerCartBtn = document.getElementById("headerCartBtn");
const headerCartCount = document.getElementById("headerCartCount");
const logoutBtn = document.getElementById("logoutBtn");

export function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

export function openModal(html) {
  modalContent.innerHTML = html;
  modalOverlay.classList.add("open");
  document.body.style.overflow = "hidden";

  // Bind close buttons
  modalContent.querySelectorAll("[data-close-modal]").forEach(btn => {
    btn.addEventListener("click", closeModal);
  });
}

export function closeModal() {
  modalOverlay.classList.remove("open");
  document.body.style.overflow = "";
}

// Close modal when clicking on backdrop
modalOverlay.addEventListener("click", (e) => {
  if (e.target === modalOverlay) {
    closeModal();
  }
});

export function confirmDialog(title, message, onConfirm) {
  openModal(`
    <div class="modal-header">
      <h3 class="modal-title font-serif">${title}</h3>
      <button class="modal-close-btn" data-close-modal>&times;</button>
    </div>
    <div class="modal-body">
      <p style="color: var(--text-muted); font-size: 0.95rem;">${message}</p>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" data-close-modal>Cancel</button>
      <button class="btn btn-danger" id="confirmActionBtn">Confirm</button>
    </div>
  `);

  document.getElementById("confirmActionBtn").addEventListener("click", async () => {
    closeModal();
    await onConfirm();
  });
}

export async function updateCartBadge() {
  const user = getCurrentUser();
  if (!user || user.role !== "buyer") {
    headerCartBtn.style.display = "none";
    return;
  }
  headerCartBtn.style.display = "flex";
  try {
    const cart = await cartApi.getCart();
    const count = cart.items.reduce((sum, item) => sum + item.quantity, 0);
    if (count > 0) {
      headerCartCount.textContent = count > 99 ? "99+" : count;
      headerCartCount.style.display = "flex";
    } else {
      headerCartCount.style.display = "none";
    }
  } catch (err) {
    headerCartCount.style.display = "none";
  }
}

function updateNavigation(user) {
  headerUserName.textContent = user.full_name;
  headerUserAvatar.textContent = user.full_name.charAt(0).toUpperCase();
  headerUserRole.textContent = user.role.toUpperCase();
  headerUserRole.className = `role-tag ${user.role}`;

  // Role based visibility
  const isBuyer = user.role === "buyer";
  const isSeller = user.role === "seller";
  const isAdmin = user.role === "admin";
  const isSellerOrAdmin = isSeller || isAdmin;

  document.querySelectorAll(".buyer-only").forEach(el => {
    el.style.display = isBuyer ? "" : "none";
  });
  document.querySelectorAll(".seller-admin-only").forEach(el => {
    el.style.display = isSellerOrAdmin ? "" : "none";
  });
  document.querySelectorAll(".admin-only").forEach(el => {
    el.style.display = isAdmin ? "" : "none";
  });

  if (isBuyer) {
    updateCartBadge();
  } else {
    headerCartBtn.style.display = "none";
  }
}

async function navigate() {
  const hash = window.location.hash.slice(1) || "shop";
  const route = hash.split("?")[0];

  const user = getCurrentUser();
  if (!user) {
    window.location.href = "index.html";
    return;
  }

  // Permission guard
  if ((route === "cart" || route === "orders") && user.role !== "buyer") {
    window.location.hash = "#shop";
    return;
  }
  if ((route === "listings" || route === "orders-received") && user.role === "buyer") {
    window.location.hash = "#shop";
    return;
  }
  if ((route === "users" || route === "import-rules" || route === "reports") && user.role !== "admin") {
    window.location.hash = "#shop";
    return;
  }

  // Update sidebar active link
  document.querySelectorAll(".nav-item").forEach(item => {
    if (item.dataset.route === route) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });

  // Render view
  const renderFn = ROUTES[route] || renderShopView;
  try {
    await renderFn(mainContent);
  } catch (err) {
    mainContent.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">⚠️</div>
        <h3>Failed to load section</h3>
        <p>${err.message}</p>
        <button class="btn btn-primary" onclick="window.location.reload()">Reload Page</button>
      </div>
    `;
  }
}

// Init application
async function initApp() {
  if (!getToken()) {
    window.location.href = "index.html";
    return;
  }

  try {
    const user = await usersApi.getMe();
    setCurrentUser(user);
    updateNavigation(user);
  } catch (err) {
    clearAuth();
    window.location.href = "index.html";
    return;
  }

  // Logout listener
  logoutBtn.addEventListener("click", async () => {
    try {
      await authApi.logout();
    } catch (e) {
      // Ignore
    } finally {
      clearAuth();
      window.location.href = "index.html";
    }
  });

  // Listen to hash changes
  window.addEventListener("hashchange", navigate);

  // Initial navigation
  await navigate();
}

window.addEventListener("DOMContentLoaded", initApp);
