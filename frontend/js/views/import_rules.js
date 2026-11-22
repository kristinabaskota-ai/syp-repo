import { importCheckApi, escapeHtml } from "../api.js";
import { openModal, closeModal, showToast, confirmDialog } from "../app.js";

export async function renderImportRulesView(container) {
  container.innerHTML = `
    <div class="section-header">
      <div>
        <h2 class="section-title">Import Regulations Management</h2>
        <p class="section-subtitle">Maintain international phytosanitary rules, CITES appendices, and prohibited species.</p>
      </div>
      <div>
        <button class="btn btn-primary" id="addRuleBtn">
          + Add New Regulation Rule
        </button>
      </div>
    </div>

    <!-- Rules Table -->
    <div class="table-container" id="rulesTableArea">
      <div class="empty-state">
        <p>Loading import rules...</p>
      </div>
    </div>
  `;

  const rulesTableArea = document.getElementById("rulesTableArea");
  const addRuleBtn = document.getElementById("addRuleBtn");

  async function loadRules() {
    rulesTableArea.innerHTML = `<div class="empty-state"><p>Loading regulations...</p></div>`;
    try {
      const rules = await importCheckApi.listRules();

      if (!rules || rules.length === 0) {
        rulesTableArea.innerHTML = `
          <div class="empty-state">
            <div class="empty-state-icon">⚖️</div>
            <h3>No rules recorded</h3>
            <p>Add international biosecurity directives to guide cross-border plant shipments.</p>
          </div>
        `;
        return;
      }

      const rowsHtml = rules.map(r => `
        <tr data-id="${r.id}">
          <td style="font-weight: 700; color: var(--primary-dark);">${escapeHtml(r.country)}</td>
          <td>
            <code>${escapeHtml(r.plant_name)}</code>
            ${r.plant_name === '*' ? '<span style="font-size: 0.75rem; color: var(--text-muted); margin-left: 0.3rem;">(Country-wide)</span>' : ''}
          </td>
          <td>
            <div style="display: flex; gap: 0.35rem; flex-wrap: wrap;">
              ${r.cites_protected ? '<span class="badge" style="background:#fff3e0; color:#e65100;">CITES</span>' : ''}
              ${r.is_banned ? '<span class="badge" style="background:#ffebee; color:#c62828;">BANNED</span>' : ''}
              ${!r.cites_protected && !r.is_banned ? '<span class="badge" style="background:#e8f5e9; color:#2e7d32;">Standard</span>' : ''}
            </div>
          </td>
          <td style="max-width: 320px; font-size: 0.82rem; color: var(--text-muted); line-height: 1.4;">
            ${escapeHtml(r.required_documents.split('\n')[0])}
            ${r.required_documents.split('\n').length > 1 ? `<em>(+${r.required_documents.split('\n').length - 1} more docs)</em>` : ''}
          </td>
          <td style="text-align: right;">
            <button class="btn btn-secondary btn-sm edit-rule-btn" data-id="${r.id}" style="margin-right: 0.35rem;">
              Edit
            </button>
            <button class="btn btn-secondary btn-sm delete-rule-btn" data-id="${r.id}" style="color: var(--danger);">
              Delete
            </button>
          </td>
        </tr>
      `).join("");

      rulesTableArea.innerHTML = `
        <table class="data-table">
          <thead>
            <tr>
              <th>Country</th>
              <th>Target Species</th>
              <th>Status Flags</th>
              <th>Document Requirements</th>
              <th style="text-align: right;">Actions</th>
            </tr>
          </thead>
          <tbody>
            ${rowsHtml}
          </tbody>
        </table>
      `;

      // Bind edit
      rulesTableArea.querySelectorAll(".edit-rule-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const ruleId = btn.dataset.id;
          const rule = rules.find(r => r.id == ruleId);
          if (rule) showRuleModal(rule);
        });
      });

      // Bind delete
      rulesTableArea.querySelectorAll(".delete-rule-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const ruleId = btn.dataset.id;
          confirmDialog(
            "Delete Regulation Rule?",
            "Are you sure you want to permanently delete this import regulation?",
            async () => {
              try {
                await importCheckApi.deleteRule(ruleId);
                showToast("Regulation deleted successfully.", "info");
                await loadRules();
              } catch (err) {
                showToast(err.message, "error");
              }
            }
          );
        });
      });

    } catch (err) {
      rulesTableArea.innerHTML = `
        <div class="empty-state">
          <p style="color: var(--danger);">Failed to load rules: ${escapeHtml(err.message)}</p>
        </div>
      `;
    }
  }

  function showRuleModal(rule = null) {
    const isEdit = rule !== null;

    openModal(`
      <div class="modal-header">
        <h3 class="modal-title font-serif">${isEdit ? 'Edit Regulation Rule' : 'Add New Regulation Rule'}</h3>
        <button class="modal-close-btn" data-close-modal>&times;</button>
      </div>
      <form id="ruleForm">
        <div class="modal-body">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label for="ruleCountry">Country</label>
              <input type="text" id="ruleCountry" class="form-input" value="${rule ? escapeHtml(rule.country) : ''}" placeholder="e.g. Nepal, United States" required minlength="2">
            </div>
            <div class="form-group">
              <label for="rulePlant">Plant Name</label>
              <input type="text" id="rulePlant" class="form-input" value="${rule ? escapeHtml(rule.plant_name) : '*'}" placeholder="* for general country rule, or species name" required>
            </div>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label for="ruleBanned">Prohibited / Banned Status</label>
              <select id="ruleBanned" class="form-select">
                <option value="false" ${rule && !rule.is_banned ? 'selected' : ''}>Allowed with Permits</option>
                <option value="true" ${rule && rule.is_banned ? 'selected' : ''}>⛔ Strictly Banned / Invasive</option>
              </select>
            </div>
            <div class="form-group">
              <label for="ruleCites">CITES Protection Status</label>
              <select id="ruleCites" class="form-select">
                <option value="false" ${rule && !rule.cites_protected ? 'selected' : ''}>Not CITES Listed</option>
                <option value="true" ${rule && rule.cites_protected ? 'selected' : ''}>⚠️ CITES Protected (Appendix I/II)</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="ruleDocs">Required Documents (One per line)</label>
            <textarea id="ruleDocs" class="form-textarea" placeholder="Phytosanitary Certificate&#10;Plant Import Permit&#10;Customs Declaration" required rows="4">${rule ? escapeHtml(rule.required_documents) : ''}</textarea>
          </div>

          <div class="form-group">
            <label for="ruleNotes">Port of Entry & Quarantine Notes (Optional)</label>
            <textarea id="ruleNotes" class="form-textarea" placeholder="Inspection stations, fumigation directives, biosecurity warnings...">${rule && rule.notes ? escapeHtml(rule.notes) : ''}</textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-close-modal>Cancel</button>
          <button type="submit" class="btn btn-primary" id="saveRuleBtn">
            ${isEdit ? 'Save Changes' : 'Create Regulation'}
          </button>
        </div>
      </form>
    `);

    document.getElementById("ruleForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        country: document.getElementById("ruleCountry").value.trim(),
        plant_name: document.getElementById("rulePlant").value.trim(),
        is_banned: document.getElementById("ruleBanned").value === "true",
        cites_protected: document.getElementById("ruleCites").value === "true",
        required_documents: document.getElementById("ruleDocs").value.trim(),
        notes: document.getElementById("ruleNotes").value.trim() || null,
      };

      const saveBtn = document.getElementById("saveRuleBtn");
      saveBtn.disabled = true;
      saveBtn.textContent = "Saving...";

      try {
        if (isEdit) {
          await importCheckApi.updateRule(rule.id, payload);
          showToast("Regulation rule updated!", "success");
        } else {
          await importCheckApi.createRule(payload);
          showToast("New regulation rule created!", "success");
        }
        closeModal();
        await loadRules();
      } catch (err) {
        showToast(err.message, "error");
        saveBtn.disabled = false;
        saveBtn.textContent = isEdit ? "Save Changes" : "Create Regulation";
      }
    });
  }

  addRuleBtn.addEventListener("click", () => showRuleModal());
  await loadRules();
}
