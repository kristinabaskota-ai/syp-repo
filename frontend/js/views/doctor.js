import { doctorApi, cartApi, getCurrentUser, escapeHtml } from "../api.js";
import { showToast, updateCartBadge } from "../app.js";

export async function renderDoctorView(container) {
  const user = getCurrentUser();
  const isBuyer = user && user.role === "buyer";

  container.innerHTML = `
    <!-- Doctor Hero -->
    <div class="doctor-hero">
      <div class="ai-badge">🩺 Intelligent Diagnostic Engine</div>
      <h2>Plant Doctor</h2>
      <p>Identify plant ailments through guided botanical symptom analysis. Treatments are ranked organic-first, with household safety filters protecting curious pets, young children, and edible crops.</p>
      <div style="margin-top: 1rem; font-size: 0.85rem; color: #ffdfd8; display: flex; align-items: center; gap: 0.5rem;">
        <span>🔬</span> <em>Note: Photo diagnosis with MobileNetV2 deep-learning classification is currently in development. Guided clinical analysis is fully operational below.</em>
      </div>
    </div>

    <!-- Wizard Steps Indicator -->
    <div class="step-indicator">
      <div class="step-item active" id="stepIndicator1">
        <div class="step-num">1</div>
        <div class="step-label">Affected Plant Part</div>
      </div>
      <div class="step-item" id="stepIndicator2">
        <div class="step-num">2</div>
        <div class="step-label">Visual Observation</div>
      </div>
      <div class="step-item" id="stepIndicator3">
        <div class="step-num">3</div>
        <div class="step-label">Household Safety</div>
      </div>
    </div>

    <!-- Wizard Step Content Container -->
    <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 2rem; box-shadow: var(--shadow-sm); margin-bottom: 2.5rem;">
      
      <!-- STEP 1: Select Part -->
      <div id="stepPartView">
        <h3 class="font-serif" style="font-size: 1.4rem; margin-bottom: 0.5rem;">Step 1: Which part of your plant shows distress?</h3>
        <p style="color: var(--text-muted); font-size: 0.92rem; margin-bottom: 1.75rem;">Select the anatomical botanical region exhibiting visible symptoms or decline.</p>

        <div class="part-selection-grid">
          <div class="part-card" data-part="leaf">
            <div class="part-icon">🍃</div>
            <div class="part-name">Leaf</div>
            <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.3rem;">Yellowing, spots, curling, webbing</div>
          </div>
          <div class="part-card" data-part="stem">
            <div class="part-icon">🎋</div>
            <div class="part-name">Stem</div>
            <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.3rem;">Mushy lesions, mealy fluff, cankers</div>
          </div>
          <div class="part-card" data-part="root">
            <div class="part-icon">🪴</div>
            <div class="part-name">Root</div>
            <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.3rem;">Black squishy roots, sulfur odor, bound</div>
          </div>
          <div class="part-card" data-part="flower">
            <div class="part-icon">🌸</div>
            <div class="part-name">Flower</div>
            <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.3rem;">Bud blast, petal discoloration, thrips</div>
          </div>
        </div>
      </div>

      <!-- STEP 2: Select Observation -->
      <div id="stepObservationView" style="display: none;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
          <div>
            <h3 class="font-serif" style="font-size: 1.4rem; margin-bottom: 0.3rem;">Step 2: What do you observe?</h3>
            <p style="color: var(--text-muted); font-size: 0.92rem;">Select the symptom matching your plant's condition.</p>
          </div>
          <button class="btn btn-secondary btn-sm" id="backToStep1Btn">&larr; Change Plant Part</button>
        </div>

        <div id="symptomsListGroup" style="display: flex; flex-direction: column; gap: 0.85rem; margin-bottom: 1.5rem;">
          <div class="empty-state">Loading symptoms...</div>
        </div>
      </div>

      <!-- STEP 3: Household Safety Switches -->
      <div id="stepSafetyView" style="display: none;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
          <div>
            <h3 class="font-serif" style="font-size: 1.4rem; margin-bottom: 0.3rem;">Step 3: Household Safety Requirements</h3>
            <p style="color: var(--text-muted); font-size: 0.92rem;">Filter remedies to guarantee safe application in your living environment.</p>
          </div>
          <button class="btn btn-secondary btn-sm" id="backToStep2Btn">&larr; Back to Observations</button>
        </div>

        <div class="safety-toggles-card">
          <div class="safety-toggle-item">
            <div class="safety-toggle-info">
              <h4>🐾 Domestic Pets in Home</h4>
              <p>Hides remedies containing systemic neurotoxins or compounds hazardous to cats and dogs (requires pet-safe certification).</p>
            </div>
            <label style="position: relative; display: inline-block; width: 48px; height: 26px;">
              <input type="checkbox" id="safetyPets" style="opacity: 0; width: 0; height: 0;">
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="safety-toggle-item">
            <div class="safety-toggle-info">
              <h4>👶 Young Children Present</h4>
              <p>Restricts harsh chemical sprays that could cause irritation upon touch or accidental oral contact.</p>
            </div>
            <label style="position: relative; display: inline-block; width: 48px; height: 26px;">
              <input type="checkbox" id="safetyChildren" style="opacity: 0; width: 0; height: 0;">
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="safety-toggle-item">
            <div class="safety-toggle-info">
              <h4>🥗 Edible Plant / Culinary Herb</h4>
              <p>Ensures treatments leave zero synthetic chemical residues on produce intended for consumption.</p>
            </div>
            <label style="position: relative; display: inline-block; width: 48px; height: 26px;">
              <input type="checkbox" id="safetyEdible" style="opacity: 0; width: 0; height: 0;">
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <button class="btn btn-primary btn-block" id="runDiagnosisBtn" style="padding: 0.9rem; font-size: 1rem;">
          🩺 Analyze Condition & Generate Treatment Plan
        </button>
      </div>

      <!-- RESULTS SECTION -->
      <div id="doctorResultsView" style="display: none; border-top: 2px dashed var(--border); padding-top: 2rem; margin-top: 1.5rem;">
        <!-- Filled dynamically -->
      </div>
    </div>

    <!-- User's Diagnostic History -->
    <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 2rem; box-shadow: var(--shadow-sm);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <h3 class="font-serif" style="font-size: 1.35rem;">Recent Diagnostic Consultations</h3>
        <button class="btn btn-secondary btn-sm" id="refreshHistoryBtn">Refresh</button>
      </div>
      <div id="doctorHistoryArea">
        <p style="color: var(--text-muted); font-size: 0.88rem;">Loading consultation history...</p>
      </div>
    </div>
  `;

  // Custom styling for toggle switches
  const toggleStyle = document.createElement("style");
  toggleStyle.textContent = `
    .toggle-slider {
      position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
      background-color: #ccc; transition: .25s; border-radius: 34px;
    }
    .toggle-slider:before {
      position: absolute; content: ""; height: 20px; width: 20px; left: 3px; bottom: 3px;
      background-color: white; transition: .25s; border-radius: 50%;
    }
    input:checked + .toggle-slider {
      background-color: var(--primary);
    }
    input:checked + .toggle-slider:before {
      transform: translateX(22px);
    }
  `;
  document.head.appendChild(toggleStyle);

  // State
  let selectedPart = null;
  let selectedSymptomId = null;

  const stepIndicator1 = document.getElementById("stepIndicator1");
  const stepIndicator2 = document.getElementById("stepIndicator2");
  const stepIndicator3 = document.getElementById("stepIndicator3");

  const stepPartView = document.getElementById("stepPartView");
  const stepObservationView = document.getElementById("stepObservationView");
  const stepSafetyView = document.getElementById("stepSafetyView");
  const doctorResultsView = document.getElementById("doctorResultsView");
  const symptomsListGroup = document.getElementById("symptomsListGroup");

  const backToStep1Btn = document.getElementById("backToStep1Btn");
  const backToStep2Btn = document.getElementById("backToStep2Btn");
  const runDiagnosisBtn = document.getElementById("runDiagnosisBtn");
  const doctorHistoryArea = document.getElementById("doctorHistoryArea");
  const refreshHistoryBtn = document.getElementById("refreshHistoryBtn");

  // Step 1: Part Selection
  document.querySelectorAll(".part-card").forEach(card => {
    card.addEventListener("click", async () => {
      document.querySelectorAll(".part-card").forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      selectedPart = card.dataset.part;

      // Update indicator
      stepIndicator1.classList.remove("active");
      stepIndicator1.classList.add("completed");
      stepIndicator2.classList.add("active");

      // Switch view
      stepPartView.style.display = "none";
      stepObservationView.style.display = "block";
      doctorResultsView.style.display = "none";

      await loadSymptomsForPart(selectedPart);
    });
  });

  backToStep1Btn.addEventListener("click", () => {
    stepIndicator2.classList.remove("active");
    stepIndicator1.classList.remove("completed");
    stepIndicator1.classList.add("active");
    stepObservationView.style.display = "none";
    stepPartView.style.display = "block";
  });

  backToStep2Btn.addEventListener("click", () => {
    stepIndicator3.classList.remove("active");
    stepIndicator2.classList.remove("completed");
    stepIndicator2.classList.add("active");
    stepSafetyView.style.display = "none";
    stepObservationView.style.display = "block";
  });

  // Load symptoms for selected part
  async function loadSymptomsForPart(part) {
    symptomsListGroup.innerHTML = `<div class="empty-state"><p>Loading symptoms for ${part}...</p></div>`;
    try {
      const symptoms = await doctorApi.getSymptoms(part);
      if (symptoms.length === 0) {
        symptomsListGroup.innerHTML = `
          <div class="empty-state">
            <p>No recorded symptoms for ${part}.</p>
          </div>
        `;
        return;
      }

      symptomsListGroup.innerHTML = symptoms.map(s => `
        <div class="symptom-choice-card" data-symptom-id="${s.id}" style="background: var(--bg-main); border: 1.5px solid var(--border); border-radius: var(--radius-md); padding: 1.1rem 1.4rem; cursor: pointer; transition: var(--transition);">
          <div style="display: flex; justify-content: space-between; align-items: baseline;">
            <strong style="font-size: 1.05rem; color: var(--primary-dark);">${escapeHtml(s.observation)}</strong>
            <span style="font-size: 0.8rem; color: var(--text-muted); text-transform: capitalize;">${s.plant_part} symptom</span>
          </div>
          <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.35rem;">
            Primary diagnosis: <em>${escapeHtml(s.diagnosis)}</em>
          </div>
        </div>
      `).join("");

      symptomsListGroup.querySelectorAll(".symptom-choice-card").forEach(c => {
        c.addEventListener("click", () => {
          symptomsListGroup.querySelectorAll(".symptom-choice-card").forEach(el => {
            el.style.borderColor = "var(--border)";
            el.style.background = "var(--bg-main)";
          });
          c.style.borderColor = "var(--primary)";
          c.style.background = "var(--primary-subtle)";
          selectedSymptomId = parseInt(c.dataset.symptomId);

          // Advance to step 3
          stepIndicator2.classList.remove("active");
          stepIndicator2.classList.add("completed");
          stepIndicator3.classList.add("active");

          stepObservationView.style.display = "none";
          stepSafetyView.style.display = "block";
        });
      });

    } catch (err) {
      symptomsListGroup.innerHTML = `
        <div class="empty-state" style="color: var(--danger);">
          <p>Failed to load symptoms: ${escapeHtml(err.message)}</p>
        </div>
      `;
    }
  }

  // Step 3: Run Diagnosis
  runDiagnosisBtn.addEventListener("click", async () => {
    if (!selectedSymptomId) {
      showToast("Please choose an observed symptom first.", "error");
      return;
    }

    const hasPets = document.getElementById("safetyPets").checked;
    const hasChildren = document.getElementById("safetyChildren").checked;
    const plantIsEdible = document.getElementById("safetyEdible").checked;

    runDiagnosisBtn.disabled = true;
    runDiagnosisBtn.textContent = "Analyzing Symptom Pathology...";

    try {
      const result = await doctorApi.diagnose({
        symptom_id: selectedSymptomId,
        has_pets: hasPets,
        has_children: hasChildren,
        plant_is_edible: plantIsEdible,
      });

      renderDiagnosisResult(result, { hasPets, hasChildren, plantIsEdible });
      await loadHistory();
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      runDiagnosisBtn.disabled = false;
      runDiagnosisBtn.textContent = "🩺 Analyze Condition & Generate Treatment Plan";
    }
  });

  function renderDiagnosisResult(result, flags) {
    doctorResultsView.style.display = "block";
    doctorResultsView.scrollIntoView({ behavior: "smooth" });

    const s = result.symptom;
    const treatments = result.safe_treatments;

    let safetyFilterNotice = "";
    if (result.hidden_treatments_count > 0) {
      safetyFilterNotice = `
        <div style="background: var(--warning-bg); border: 1.5px solid #ffe082; color: #744210; border-radius: var(--radius-md); padding: 0.9rem 1.25rem; margin-bottom: 1.5rem; font-size: 0.88rem; display: flex; align-items: center; gap: 0.75rem;">
          <span style="font-size: 1.4rem;">🛡️</span>
          <div>
            <strong>${result.hidden_treatments_count} unsafe treatment(s) were hidden</strong> based on your household parameters (${flags.hasPets ? '🐾 Pets, ' : ''}${flags.hasChildren ? '👶 Children, ' : ''}${flags.plantIsEdible ? '🥗 Edible, ' : ''}).
          </div>
        </div>
      `;
    }

    let nurseryAdviceHtml = "";
    if (result.household_advice) {
      nurseryAdviceHtml = `
        <div style="background: #fce4ec; border: 1.5px solid #f48fb1; color: #880e4f; border-radius: var(--radius-md); padding: 1.25rem; margin-bottom: 1.5rem;">
          <h4 style="font-size: 1.05rem; margin-bottom: 0.4rem;">⚠️ Nursery Consultation Recommended</h4>
          <p style="font-size: 0.92rem; line-height: 1.5;">${escapeHtml(result.household_advice)}</p>
        </div>
      `;
    }

    const treatmentsHtml = treatments.map((t, idx) => {
      const typeClass = t.treatment_type.toLowerCase();
      const badgeClass = `treatment-type-badge ${typeClass}`;
      const prod = t.product;

      let linkedProductHtml = "";
      if (prod) {
        linkedProductHtml = `
          <div class="treatment-linked-product">
            <div>
              <div style="font-size: 0.78rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">
                Recommended Shop Product
              </div>
              <strong style="font-size: 0.95rem; color: var(--primary-dark);">${escapeHtml(prod.name)}</strong>
              <div style="font-size: 0.85rem; color: var(--primary); font-weight: 700;">
                NPR ${prod.price.toLocaleString()} &bull; <span style="font-weight: 500; color: var(--text-muted);">${prod.stock} in stock</span>
              </div>
            </div>
            ${isBuyer && prod.stock > 0 ? `
              <button class="btn btn-outline btn-sm add-treatment-prod-btn" data-id="${prod.id}" data-name="${escapeHtml(prod.name)}">
                Add to Cart
              </button>
            ` : ""}
          </div>
        `;
      }

      return `
        <div class="treatment-card type-${typeClass}">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 0.6rem;">
              <span style="font-weight: 700; color: var(--text-muted); font-size: 0.88rem;">#${idx + 1}</span>
              <span class="${badgeClass}">${t.treatment_type}</span>
            </div>
            <div style="display: flex; gap: 0.4rem; font-size: 0.75rem;">
              ${t.pet_safe ? `<span class="badge badge-pet-safe">🐾 Pet Safe</span>` : ''}
              ${t.child_safe ? `<span class="badge" style="background:#e1f5fe; color:#0277bd;">👶 Child Safe</span>` : ''}
              ${t.edible_safe ? `<span class="badge" style="background:#e8f5e9; color:#2e7d32;">🥗 Food Safe</span>` : ''}
            </div>
          </div>
          <h4 style="font-size: 1.15rem; color: var(--primary-dark); font-family: var(--font-serif);">${escapeHtml(t.name)}</h4>
          <p style="font-size: 0.9rem; line-height: 1.5; color: var(--text-primary);">${escapeHtml(t.instructions)}</p>
          ${linkedProductHtml}
        </div>
      `;
    }).join("");

    doctorResultsView.innerHTML = `
      <div style="margin-bottom: 1.75rem;">
        <span class="badge" style="background: var(--primary); color: #fff; margin-bottom: 0.5rem;">Diagnostic Report</span>
        <h3 class="font-serif" style="font-size: 1.8rem; color: var(--primary-dark); margin: 0.3rem 0;">${escapeHtml(s.diagnosis)}</h3>
        <p style="font-size: 0.95rem; color: var(--text-muted);">Affecting: <strong>${escapeHtml(s.plant_part.toUpperCase())}</strong> &bull; Observed: <em>"${escapeHtml(s.observation)}"</em></p>
      </div>

      <div style="background: var(--bg-main); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.25rem; margin-bottom: 1.5rem;">
        <h4 style="font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 0.4rem;">Botanical Etiology & Cause</h4>
        <p style="font-size: 0.92rem; line-height: 1.55; color: var(--text-primary);">${escapeHtml(s.cause)}</p>
      </div>

      ${safetyFilterNotice}
      ${nurseryAdviceHtml}

      <div style="margin-bottom: 1.25rem;">
        <h4 class="font-serif" style="font-size: 1.3rem;">Ranked Remedies (Organic First &bull; Non-Chemical &bull; Chemical)</h4>
        <p style="font-size: 0.85rem; color: var(--text-muted);">Remedies ranked according to environmental safety and organic priority.</p>
      </div>

      <div>
        ${treatmentsHtml || '<p style="color: var(--text-muted);">No remedies available under the selected constraints.</p>'}
      </div>
    `;

    // Bind Add to Cart for linked products
    doctorResultsView.querySelectorAll(".add-treatment-prod-btn").forEach(btn => {
      btn.addEventListener("click", async () => {
        const prodId = parseInt(btn.dataset.id);
        const name = btn.dataset.name;
        try {
          await cartApi.addToCart(prodId, 1);
          showToast(`Added ${name} to cart!`, "success");
          await updateCartBadge();
        } catch (err) {
          showToast(err.message, "error");
        }
      });
    });
  }

  // Load past history
  async function loadHistory() {
    try {
      const history = await doctorApi.getHistory();
      if (!history || history.length === 0) {
        doctorHistoryArea.innerHTML = `<p style="color: var(--text-muted); font-size: 0.88rem;">No past consultations found.</p>`;
        return;
      }

      doctorHistoryArea.innerHTML = history.slice(0, 5).map(h => {
        const dt = new Date(h.created_at).toLocaleDateString("en-US", {
          month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
        });
        return `
          <div style="background: var(--bg-main); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 0.85rem 1.1rem; margin-bottom: 0.65rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
            <div>
              <strong style="color: var(--primary-dark);">${escapeHtml(h.diagnosis)}</strong>
              <div style="font-size: 0.82rem; color: var(--text-muted);">
                ${escapeHtml(h.plant_part.toUpperCase())}: "${escapeHtml(h.observation)}"
              </div>
            </div>
            <div style="font-size: 0.78rem; color: var(--text-light); text-align: right;">
              <div>${dt}</div>
              <div style="margin-top: 0.2rem;">
                ${h.has_pets ? '🐾 ' : ''}${h.has_children ? '👶 ' : ''}${h.plant_is_edible ? '🥗' : ''}
              </div>
            </div>
          </div>
        `;
      }).join("");

    } catch (err) {
      doctorHistoryArea.innerHTML = `<p style="color: var(--danger); font-size: 0.85rem;">Error loading history: ${escapeHtml(err.message)}</p>`;
    }
  }

  refreshHistoryBtn.addEventListener("click", loadHistory);
  await loadHistory();
}
