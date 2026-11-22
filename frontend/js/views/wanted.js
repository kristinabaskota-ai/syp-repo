import { wantedApi, getCurrentUser, escapeHtml } from "../api.js";
import { openModal, closeModal, showToast, confirmDialog } from "../app.js";

export async function renderWantedView(container) {
  const user = getCurrentUser();
  const isBuyer = user && user.role === "buyer";
  const isSeller = user && (user.role === "seller" || user.role === "admin");

  container.innerHTML = `
    <div class="section-header">
      <div>
        <h2 class="section-title">Wanted Plant Board</h2>
        <p class="section-subtitle">Sourcing exchange connecting collectors with verified specialist nurseries.</p>
      </div>
      <div>
        ${isBuyer ? `
          <button class="btn btn-primary" id="postWantedBtn">
            + Post Wanted Plant
          </button>
        ` : ''}
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div style="font-weight: 600; font-size: 0.9rem; color: var(--text-muted);">Filter by Status:</div>
      <div style="display: flex; gap: 0.5rem;">
        <button class="btn btn-sm btn-secondary filter-status-btn active" data-status="">All</button>
        <button class="btn btn-sm btn-secondary filter-status-btn" data-status="open">Open Requests</button>
        <button class="btn btn-sm btn-secondary filter-status-btn" data-status="fulfilled">Fulfilled</button>
        <button class="btn btn-sm btn-secondary filter-status-btn" data-status="closed">Closed</button>
      </div>
    </div>

    <!-- Requests Container -->
    <div id="wantedFeedArea">
      <div class="empty-state">
        <p>Loading wanted requests...</p>
      </div>
    </div>
  `;

  let currentStatusFilter = "";

  const wantedFeedArea = document.getElementById("wantedFeedArea");
  const postWantedBtn = document.getElementById("postWantedBtn");

  // Filter status buttons
  document.querySelectorAll(".filter-status-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-status-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentStatusFilter = btn.dataset.status;
      loadRequests();
    });
  });

  async function loadRequests() {
    wantedFeedArea.innerHTML = `<div class="empty-state"><p>Loading wanted requests...</p></div>`;
    try {
      const requests = await wantedApi.listRequests(currentStatusFilter || null);

      if (!requests || requests.length === 0) {
        wantedFeedArea.innerHTML = `
          <div class="empty-state">
            <div class="empty-state-icon">🌱</div>
            <h3>No requests found</h3>
            <p>There are no plant sourcing requests matching this criteria.</p>
          </div>
        `;
        return;
      }

      wantedFeedArea.innerHTML = requests.map(r => {
        const dateStr = new Date(r.created_at).toLocaleDateString("en-US", {
          year: "numeric", month: "short", day: "numeric"
        });

        const statusBadges = {
          "open": "background: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9;",
          "fulfilled": "background: #e3f2fd; color: #1565c0; border: 1px solid #bbdefb;",
          "closed": "background: #eceff1; color: #546e7a; border: 1px solid #cfd8dc;",
        };

        const isOwner = user && r.buyer_id === user.id;
        const isOpen = r.status === "open";
        const offerCount = r.offers ? r.offers.length : 0;

        return `
          <div class="wanted-card" data-id="${r.id}" style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.5rem; margin-bottom: 1.25rem; box-shadow: var(--shadow-sm);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
              <div>
                <span class="badge" style="${statusBadges[r.status] || ''}; margin-bottom: 0.4rem;">
                  ${r.status.toUpperCase()}
                </span>
                <h3 style="font-family: var(--font-serif); font-size: 1.3rem; color: var(--primary-dark); margin: 0.2rem 0;">
                  ${escapeHtml(r.plant_name)}
                </h3>
                <div style="font-size: 0.82rem; color: var(--text-muted);">
                  Posted by <strong>${escapeHtml(r.buyer_name || 'Collector')}</strong> on ${dateStr} &bull; Delivery: <strong>${escapeHtml(r.destination_country)}</strong>
                </div>
              </div>

              <!-- Action buttons -->
              <div style="display: flex; gap: 0.5rem;">
                ${isOwner && isOpen ? `
                  <button class="btn btn-secondary btn-sm close-request-btn" data-id="${r.id}">
                    Close Request
                  </button>
                ` : ""}

                ${isOwner ? `
                  <button class="btn btn-primary btn-sm view-offers-btn" data-id="${r.id}">
                    View Offers (${offerCount})
                  </button>
                ` : (isSeller && isOpen ? `
                  <button class="btn btn-accent btn-sm make-offer-btn" data-id="${r.id}" data-name="${escapeHtml(r.plant_name)}">
                    Submit Offer
                  </button>
                ` : "")}
              </div>
            </div>

            <p style="font-size: 0.92rem; line-height: 1.5; color: var(--text-primary); margin-bottom: 1rem;">
              ${escapeHtml(r.details)}
            </p>

            ${(isSeller && r.offers && r.offers.length > 0) ? `
              <div style="background: var(--bg-main); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 0.75rem 1rem; font-size: 0.85rem; display: flex; justify-content: space-between; align-items: center;">
                <span>Your submitted offer: <strong>NPR ${r.offers[0].price.toLocaleString()}</strong> (${r.offers[0].status})</span>
                <span class="badge" style="background:#e3f2fd; color:#1565c0;">${r.offers[0].status.toUpperCase()}</span>
              </div>
            ` : ""}
          </div>
        `;
      }).join("");

      // Bind close button
      wantedFeedArea.querySelectorAll(".close-request-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const reqId = btn.dataset.id;
          confirmDialog(
            "Close Request?",
            "Are you sure you want to close this wanted plant request? Nurseries will no longer be able to submit offers.",
            async () => {
              try {
                await wantedApi.closeRequest(reqId);
                showToast("Request closed successfully.", "info");
                await loadRequests();
              } catch (err) {
                showToast(err.message, "error");
              }
            }
          );
        });
      });

      // Bind View Offers button (Buyer view)
      wantedFeedArea.querySelectorAll(".view-offers-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
          const reqId = btn.dataset.id;
          try {
            const req = await wantedApi.getRequest(reqId);
            showOffersModal(req);
          } catch (err) {
            showToast(err.message, "error");
          }
        });
      });

      // Bind Make Offer button (Seller view)
      wantedFeedArea.querySelectorAll(".make-offer-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const reqId = btn.dataset.id;
          const plantName = btn.dataset.name;
          showMakeOfferModal(reqId, plantName);
        });
      });

    } catch (err) {
      wantedFeedArea.innerHTML = `
        <div class="empty-state">
          <p style="color: var(--danger);">Failed to load requests: ${escapeHtml(err.message)}</p>
        </div>
      `;
    }
  }

  function showOffersModal(req) {
    const offers = req.offers || [];
    const isOpen = req.status === "open";

    const offersHtml = offers.length === 0 ? `
      <div class="empty-state" style="padding: 1.5rem;">
        <p>No nursery offers submitted yet. Check back soon!</p>
      </div>
    ` : offers.map(o => `
      <div style="background: var(--bg-main); border: 1.5px solid var(--border); border-radius: var(--radius-md); padding: 1.25rem; margin-bottom: 0.9rem;">
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem;">
          <div>
            <strong style="font-size: 1.05rem; color: var(--primary-dark);">${escapeHtml(o.seller_name || 'Nursery')}</strong>
            <span class="badge" style="margin-left: 0.5rem; font-size: 0.72rem; ${o.status === 'accepted' ? 'background:#e8f5e9; color:#2e7d32;' : (o.status === 'rejected' ? 'background:#ffebee; color:#c62828;' : 'background:#fff8e1; color:#b7791f;')}">
              ${o.status.toUpperCase()}
            </span>
          </div>
          <div style="font-weight: 700; font-size: 1.2rem; color: var(--primary);">
            NPR ${o.price.toLocaleString()}
          </div>
        </div>
        <p style="font-size: 0.9rem; line-height: 1.45; color: var(--text-primary); margin-bottom: 0.75rem;">
          ${escapeHtml(o.message)}
        </p>
        ${isOpen && o.status === 'pending' ? `
          <button class="btn btn-primary btn-sm accept-offer-btn" data-req-id="${req.id}" data-offer-id="${o.id}">
            Accept This Offer
          </button>
        ` : ''}
      </div>
    `).join("");

    openModal(`
      <div class="modal-header">
        <div>
          <h3 class="modal-title font-serif">Offers for "${escapeHtml(req.plant_name)}"</h3>
          <div style="font-size: 0.82rem; color: var(--text-muted);">Status: ${req.status.toUpperCase()}</div>
        </div>
        <button class="modal-close-btn" data-close-modal>&times;</button>
      </div>
      <div class="modal-body">
        ${offersHtml}
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" data-close-modal>Close</button>
      </div>
    `);

    // Bind Accept buttons
    document.querySelectorAll(".accept-offer-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const rId = btn.dataset.reqId;
        const oId = btn.dataset.offerId;
        confirmDialog(
          "Accept Offer?",
          "Accepting this offer will mark this sourcing request as fulfilled and automatically reject other competing offers. Proceed?",
          async () => {
            try {
              await wantedApi.acceptOffer(rId, oId);
              closeModal();
              showToast("Offer accepted! Request fulfilled.", "success");
              await loadRequests();
            } catch (err) {
              showToast(err.message, "error");
            }
          }
        );
      });
    });
  }

  function showMakeOfferModal(reqId, plantName) {
    openModal(`
      <div class="modal-header">
        <h3 class="modal-title font-serif">Submit Nursery Offer</h3>
        <button class="modal-close-btn" data-close-modal>&times;</button>
      </div>
      <form id="makeOfferForm">
        <div class="modal-body">
          <div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 1.25rem;">
            Offering for request: <strong>${escapeHtml(plantName)}</strong>
          </div>

          <div class="form-group">
            <label for="offerPrice">Offer Price (NPR)</label>
            <input type="number" id="offerPrice" class="form-input" placeholder="e.g. 15000" min="1" step="0.5" required>
          </div>

          <div class="form-group">
            <label for="offerMessage">Offer Details & Specimen Condition</label>
            <textarea id="offerMessage" class="form-textarea" placeholder="Describe the plant size, rooting state, leaf count, and health guarantees..." required minlength="5"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-close-modal>Cancel</button>
          <button type="submit" class="btn btn-primary" id="confirmOfferBtn">Submit Offer</button>
        </div>
      </form>
    `);

    document.getElementById("makeOfferForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const price = parseFloat(document.getElementById("offerPrice").value);
      const message = document.getElementById("offerMessage").value.trim();
      const submitBtn = document.getElementById("confirmOfferBtn");

      submitBtn.disabled = true;
      submitBtn.textContent = "Submitting...";

      try {
        await wantedApi.makeOffer(reqId, { price, message });
        closeModal();
        showToast("Your offer has been submitted to the buyer!", "success");
        await loadRequests();
      } catch (err) {
        showToast(err.message, "error");
        submitBtn.disabled = false;
        submitBtn.textContent = "Submit Offer";
      }
    });
  }

  // Post Wanted Plant button (buyer only)
  if (postWantedBtn) {
    postWantedBtn.addEventListener("click", () => {
      openModal(`
        <div class="modal-header">
          <h3 class="modal-title font-serif">Post Wanted Plant Request</h3>
          <button class="modal-close-btn" data-close-modal>&times;</button>
        </div>
        <form id="createWantedForm">
          <div class="modal-body">
            <div class="form-group">
              <label for="wantedPlantName">Plant Common or Scientific Name</label>
              <input type="text" id="wantedPlantName" class="form-input" placeholder="e.g. Variegated Monstera Deliciosa (Large Form)" required minlength="2">
            </div>

            <div class="form-group">
              <label for="wantedCountry">Destination Country</label>
              <input type="text" id="wantedCountry" class="form-input" value="Nepal" required>
            </div>

            <div class="form-group">
              <label for="wantedDetails">Details (Cuttings, Variegation, Size, Budget)</label>
              <textarea id="wantedDetails" class="form-textarea" placeholder="Explain the specific characteristics you are seeking..." required minlength="5"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-close-modal>Cancel</button>
            <button type="submit" class="btn btn-primary" id="submitWantedBtn">Post Request</button>
          </div>
        </form>
      `);

      document.getElementById("createWantedForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const plant_name = document.getElementById("wantedPlantName").value.trim();
        const destination_country = document.getElementById("wantedCountry").value.trim();
        const details = document.getElementById("wantedDetails").value.trim();
        const submitBtn = document.getElementById("submitWantedBtn");

        submitBtn.disabled = true;
        submitBtn.textContent = "Posting...";

        try {
          await wantedApi.createRequest({ plant_name, destination_country, details });
          closeModal();
          showToast("Wanted plant request published to the board!", "success");
          await loadRequests();
        } catch (err) {
          showToast(err.message, "error");
          submitBtn.disabled = false;
          submitBtn.textContent = "Post Request";
        }
      });
    });
  }

  await loadRequests();
}
