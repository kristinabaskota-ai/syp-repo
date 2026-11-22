/**
 * RareRoot API Client
 * Automatically connects to backend at http://127.0.0.1:8000
 * Supports Live Server on any other port.
 */
const API_BASE = (window.location.port === "8000" || window.location.port === "")
  ? ""
  : "http://127.0.0.1:8000";

const TOKEN_KEY = "rareroot_token";
const USER_KEY = "rareroot_user";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export function getCurrentUser() {
  const userStr = localStorage.getItem(USER_KEY);
  try {
    return userStr ? JSON.parse(userStr) : null;
  } catch (e) {
    return null;
  }
}

export function setCurrentUser(user) {
  if (user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  } else {
    localStorage.removeItem(USER_KEY);
  }
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

export async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = { ...options.headers };

  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (options.body && typeof options.body === "object" && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(options.body);
  }

  const response = await fetch(url, { ...options, headers });

  if (response.status === 401) {
    // Session expired or revoked
    clearAuth();
    if (!window.location.pathname.endsWith("index.html") && !window.location.pathname.endsWith("/")) {
      window.location.href = "index.html";
    }
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || "Session expired. Please log in again.");
  }

  if (!response.ok) {
    let errorMsg = `Request failed (${response.status})`;
    try {
      const errData = await response.json();
      if (errData.detail) {
        if (typeof errData.detail === "string") {
          errorMsg = errData.detail;
        } else if (Array.isArray(errData.detail)) {
          errorMsg = errData.detail.map(e => e.msg).join(", ");
        }
      }
    } catch (e) {
      // Non-json response
    }
    throw new Error(errorMsg);
  }

  if (response.status === 204) {
    return null;
  }

  return await response.json();
}

// Domain API endpoints
export const authApi = {
  register: (data) => apiRequest("/auth/register", { method: "POST", body: data }),
  login: (data) => apiRequest("/auth/login", { method: "POST", body: data }),
  logout: () => apiRequest("/auth/logout", { method: "POST" }),
  changePassword: (data) => apiRequest("/auth/change-password", { method: "POST", body: data }),
  forgotPassword: (data) => apiRequest("/auth/forgot-password", { method: "POST", body: data }),
  resetPassword: (data) => apiRequest("/auth/reset-password", { method: "POST", body: data }),
};

export const usersApi = {
  getMe: () => apiRequest("/users/me"),
  updateMe: (data) => apiRequest("/users/me", { method: "PATCH", body: data }),
  listUsers: () => apiRequest("/users"),
  updateRole: (userId, role) => apiRequest(`/users/${userId}/role`, { method: "PATCH", body: { role } }),
  approveSeller: (userId, isApproved) => apiRequest(`/users/${userId}/approve`, { method: "PATCH", body: { is_approved: isApproved } }),
  updateStatus: (userId, isActive) => apiRequest(`/users/${userId}/status`, { method: "PATCH", body: { is_active: isActive } }),
};

export const productsApi = {
  getCategories: () => apiRequest("/products/categories"),
  listProducts: (params = {}) => {
    const query = new URLSearchParams();
    if (params.search) query.append("search", params.search);
    if (params.category_id) query.append("category_id", params.category_id);
    if (params.light_requirement) query.append("light_requirement", params.light_requirement);
    if (params.pet_safe !== undefined && params.pet_safe !== "") query.append("pet_safe", params.pet_safe);
    if (params.tree_purpose) query.append("tree_purpose", params.tree_purpose);
    if (params.include_inactive) query.append("include_inactive", "true");
    const qs = query.toString();
    return apiRequest(`/products${qs ? `?${qs}` : ""}`);
  },
  getSellerProducts: () => apiRequest("/products/seller/me"),
  getProduct: (id) => apiRequest(`/products/${id}`),
  createProduct: (data) => apiRequest("/products", { method: "POST", body: data }),
  updateProduct: (id, data) => apiRequest(`/products/${id}`, { method: "PUT", body: data }),
  deleteProduct: (id) => apiRequest(`/products/${id}`, { method: "DELETE" }),
  toggleActive: (id) => apiRequest(`/products/${id}/toggle-active`, { method: "PATCH" }),
};

export const cartApi = {
  getCart: () => apiRequest("/cart"),
  addToCart: (productId, quantity = 1) => apiRequest("/cart", { method: "POST", body: { product_id: productId, quantity } }),
  updateQuantity: (itemId, quantity) => apiRequest(`/cart/${itemId}`, { method: "PUT", body: { quantity } }),
  removeItem: (itemId) => apiRequest(`/cart/${itemId}`, { method: "DELETE" }),
  clearCart: () => apiRequest("/cart", { method: "DELETE" }),
};

export const ordersApi = {
  checkout: (data) => apiRequest("/orders/checkout", { method: "POST", body: data }),
  buyNow: (data) => apiRequest("/orders/buy-now", { method: "POST", body: data }),
  getMyOrders: () => apiRequest("/orders/my"),
  getReceivedOrders: () => apiRequest("/orders/received"),
  getAllOrders: () => apiRequest("/orders"),
  getOrderDetail: (id) => apiRequest(`/orders/${id}`),
  updateStatus: (id, status) => apiRequest(`/orders/${id}/status`, { method: "PATCH", body: { status } }),
  cancelOrder: (id) => apiRequest(`/orders/${id}/cancel`, { method: "PATCH" }),
};

export const wantedApi = {
  listRequests: (status = null) => {
    const qs = status ? `?status=${encodeURIComponent(status)}` : "";
    return apiRequest(`/wanted${qs}`);
  },
  createRequest: (data) => apiRequest("/wanted", { method: "POST", body: data }),
  getRequest: (id) => apiRequest(`/wanted/${id}`),
  closeRequest: (id) => apiRequest(`/wanted/${id}/close`, { method: "PATCH" }),
  makeOffer: (requestId, data) => apiRequest(`/wanted/${requestId}/offers`, { method: "POST", body: data }),
  getOffers: (requestId) => apiRequest(`/wanted/${requestId}/offers`),
  acceptOffer: (requestId, offerId) => apiRequest(`/wanted/${requestId}/offers/${offerId}/accept`, { method: "POST" }),
};

export const importCheckApi = {
  check: (country, plantName = "") => {
    const query = new URLSearchParams({ country });
    if (plantName) query.append("plant_name", plantName);
    return apiRequest(`/import-check?${query.toString()}`);
  },
  listRules: (country = "") => {
    const qs = country ? `?country=${encodeURIComponent(country)}` : "";
    return apiRequest(`/import-rules${qs}`);
  },
  createRule: (data) => apiRequest("/import-rules", { method: "POST", body: data }),
  updateRule: (id, data) => apiRequest(`/import-rules/${id}`, { method: "PUT", body: data }),
  deleteRule: (id) => apiRequest(`/import-rules/${id}`, { method: "DELETE" }),
};

export const doctorApi = {
  getParts: () => apiRequest("/doctor/parts"),
  getSymptoms: (part = "") => {
    const qs = part ? `?plant_part=${encodeURIComponent(part)}` : "";
    return apiRequest(`/doctor/symptoms${qs}`);
  },
  diagnose: (data) => apiRequest("/doctor/diagnose", { method: "POST", body: data }),
  getHistory: () => apiRequest("/doctor/history"),
};

export const reportsApi = {
  getReports: () => apiRequest("/reports"),
};
