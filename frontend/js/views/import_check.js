import { importCheckApi, escapeHtml } from "../api.js";
import { showToast } from "../app.js";

export async function renderImportCheckView(container) {
  container.innerHTML = `
    <div class="section-header">
      <div>
        <h2 class="section-title">Import Document Checker</h2>
        <p class="section-subtitle">Verify cross-border phytosanitary permits, CITES appendices, and biosecurity clearances.</p>
      </div>
    </div>

    <!-- Query Card -->
    <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 2rem; box-shadow: var(--shadow-sm); margin-bottom: 2rem;">
      <form id="importCheckForm">
        <div style="display: grid; grid-template-columns: 1fr 1.5fr auto; gap: 1.25rem; align-items: flex-end;">
          <div class="form-group" style="margin-bottom: 0;">
            <label for="checkCountry">Destination Country</label>
            <select id="checkCountry" class="form-select" required>
              <option value="Nepal">Nepal</option>
              <option value="India">India</option>
              <option value="United States">United States</option>
              <option value="United Kingdom">United Kingdom</option>
              <option value="Australia">Australia</option>
              <option value="custom">Other Country...</option>
            </select>
            <input type="text" id="checkCustomCountry" class="form-input" placeholder="Type country name..." style="display: none; margin-top: 0.5rem;">
          </div>

          <div class="form-group" style="margin-bottom: 0;">
            <label for="checkPlant">Plant Species or Genus (Optional)</label>
            <input type="text" id="checkPlant" class="form-input" placeholder="e.g. Orchid, Paphiopedilum, Cycad, Cactus, Water Hyacinth">
            <div class="form-hint">Leave blank for general country requirements, or test "orchid", "paphiopedilum", or "water hyacinth".</div>
          </div>

          <button type="submit" class="btn btn-primary" id="runCheckBtn" style="padding: 0.75rem 1.75rem;">
            🔍 Check Rules
          </button>
        </div>
      </form>
    </div>

    <!-- Results Display Area -->
    <div id="checkResultsArea">
      <div class="empty-state">
        <div class="empty-state-icon">📜</div>
        <h3>Ready for Biosecurity Analysis</h3>
        <p>Select your destination country and optional plant species above to review mandatory paperwork and CITES protections.</p>
      </div>
    </div>
  `;

  const form = document.getElementById("importCheckForm");
  const checkCountry = document.getElementById("checkCountry");
  const checkCustomCountry = document.getElementById("checkCustomCountry");
  const checkPlant = document.getElementById("checkPlant");
  const checkResultsArea = document.getElementById("checkResultsArea");

  checkCountry.addEventListener("change", () => {
    if (checkCountry.value === "custom") {
      checkCustomCountry.style.display = "block";
      checkCustomCountry.required = true;
      checkCustomCountry.focus();
    } else {
      checkCustomCountry.style.display = "none";
      checkCustomCountry.required = false;
    }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const country = (checkCountry.value === "custom" ? checkCustomCountry.value : checkCountry.value).trim();
    const plant = checkPlant.value.trim();

    checkResultsArea.innerHTML = `
      <div class="empty-state">
        <p>Analyzing import regulations for ${escapeHtml(country)}...</p>
      </div>
    `;

    try {
      const res = await importCheckApi.check(country, plant);
      renderCheckResult(res);
    } catch (err) {
      checkResultsArea.innerHTML = `
        <div class="empty-state">
          <p style="color: var(--danger);">Error checking rules: ${escapeHtml(err.message)}</p>
        </div>
      `;
    }
  });

  function renderCheckResult(res) {
    if (!res.country_found) {
      checkResultsArea.innerHTML = `
        <div class="import-check-box">
          <div class="alert-banner info">
            <span style="font-size: 1.5rem;">ℹ️</span>
            <div>
              <h4 style="font-size: 1.05rem; margin-bottom: 0.2rem;">Country Not in Registered Database</h4>
              <p style="font-size: 0.92rem;">${escapeHtml(res.notes[0] || 'No specific rules found.')}</p>
            </div>
          </div>
          <div class="disclaimer-banner">
            ${escapeHtml(res.disclaimer)}
          </div>
        </div>
      `;
      return;
    }

    let bannedBanner = "";
    if (res.is_banned) {
      bannedBanner = `
        <div class="alert-banner banned">
          <span style="font-size: 1.8rem;">⛔</span>
          <div>
            <h4 style="font-size: 1.15rem; margin-bottom: 0.3rem;">ENTRY STRICTLY PROHIBITED (Banned / Noxious Invasive Weed)</h4>
            <p style="font-size: 0.92rem; line-height: 1.5;">
              This plant species is categorized as a prohibited noxious pest, quarantine threat, or invasive bio-hazard in <strong>${escapeHtml(res.country)}</strong>. Commercial or personal import is strictly unlawful and shipments will be confiscated and destroyed at customs.
            </p>
          </div>
        </div>
      `;
    }

    let citesBanner = "";
    if (res.cites_protected) {
      citesBanner = `
        <div class="alert-banner cites">
          <span style="font-size: 1.8rem;">⚠️</span>
          <div>
            <h4 style="font-size: 1.15rem; margin-bottom: 0.3rem;">CITES PROTECTED SPECIES (Appendix I / II Listed)</h4>
            <p style="font-size: 0.92rem; line-height: 1.5;">
              This specimen falls under the Convention on International Trade in Endangered Species of Wild Fauna and Flora (CITES). 
              International movement requires an official <strong>CITES Export Permit</strong> from the country of origin and an authorized <strong>CITES Import Permit</strong> before shipping.
            </p>
          </div>
        </div>
      `;
    }

    const docsListHtml = res.required_documents.map(doc => `
      <li>
        <span style="color: var(--primary); font-weight: 700;">✓</span>
        <span>${escapeHtml(doc)}</span>
      </li>
    `).join("");

    const notesHtml = res.notes.map(note => `
      <p style="font-size: 0.9rem; line-height: 1.5; margin-bottom: 0.5rem; color: var(--text-primary);">&bull; ${escapeHtml(note)}</p>
    `).join("");

    checkResultsArea.innerHTML = `
      <div class="import-check-box">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.5rem;">
          <div>
            <span class="badge" style="background: var(--primary); color: #fff;">Import Compliance Summary</span>
            <h3 class="font-serif" style="font-size: 1.7rem; margin-top: 0.3rem;">
              Destination: ${escapeHtml(res.country)}
            </h3>
            <div style="font-size: 0.9rem; color: var(--text-muted);">
              Species analyzed: <strong>${escapeHtml(res.plant_name || 'All general live plant imports (*)')}</strong>
            </div>
          </div>
        </div>

        ${bannedBanner}
        ${citesBanner}

        <div style="margin: 1.5rem 0;">
          <h4 style="font-size: 1.1rem; color: var(--primary-dark); margin-bottom: 0.6rem;">
            Mandatory Import Documentation & Procedures
          </h4>
          <ul class="docs-checklist">
            ${docsListHtml || '<li>No specific document rules recorded.</li>'}
          </ul>
        </div>

        ${res.notes.length > 0 ? `
          <div style="background: var(--bg-main); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 1rem 1.25rem; margin-top: 1.5rem;">
            <h5 style="font-size: 0.82rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.5rem;">
              Quarantine Authority Notes & Inspection Posts
            </h5>
            ${notesHtml}
          </div>
        ` : ''}

        <div class="disclaimer-banner">
          ${escapeHtml(res.disclaimer)}
        </div>
      </div>
    `;
  }
}
