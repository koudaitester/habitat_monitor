const CATEGORY_LABELS = {
  normal_chlorella: "Normal chlorella",
  diatom: "Diatom",
  cyanobacteria: "Cyanobacteria",
  other_harmful_algae: "Other harmful algae",
};

const state = {
  observations: [],
};

const elements = {
  alert: document.querySelector("#page-alert"),
  categoryBreakdown: document.querySelector("#category-breakdown"),
  confidenceInput: document.querySelector("#confidence-input"),
  confidenceValue: document.querySelector("#confidence-value"),
  dialog: document.querySelector("#observation-dialog"),
  form: document.querySelector("#observation-form"),
  formError: document.querySelector("#form-error"),
  latest: document.querySelector("#metric-latest"),
  observationCount: document.querySelector("#observation-count"),
  rows: document.querySelector("#observation-rows"),
  search: document.querySelector("#search-input"),
  statusFilter: document.querySelector("#status-filter"),
  systemState: document.querySelector("#system-state"),
  total: document.querySelector("#metric-total"),
  review: document.querySelector("#metric-review"),
  attention: document.querySelector("#metric-attention"),
  submitButton: document.querySelector("#submit-button"),
  atmosphereView: document.querySelector("#atmosphere-view"),
  overviewView: document.querySelector("#overview-view"),
  navItems: document.querySelectorAll(".nav-item[data-view]"),
  breadcrumb: document.querySelector(".breadcrumb strong"),
  priorityAlert: document.querySelector("#atmosphere-priority-alert"),
  atmosphereFeedPill: document.querySelector("#atmosphere-feed-pill"),
  atmosphereFeedLabel: document.querySelector("#atmosphere-feed-label"),
  atmosphereMode: document.querySelector("#atmosphere-mode"),
  atmosphereModeDetail: document.querySelector("#atmosphere-mode-detail"),
  atmosphereModeIndicator: document.querySelector("#mode-indicator"),
  atmospherePhase: document.querySelector("#atmosphere-phase"),
  atmosphereDuration: document.querySelector("#atmosphere-duration"),
  atmosphereConfidence: document.querySelector("#atmosphere-confidence"),
  atmosphereSampledAt: document.querySelector("#atmosphere-sampled-at"),
  atmosphereAlertPanel: document.querySelector("#atmosphere-alert-panel"),
  atmosphereAlertContent: document.querySelector("#atmosphere-alert-content"),
  atmosphereAlertList: document.querySelector("#atmosphere-alert-list"),
  atmosphereTrends: document.querySelector("#atmosphere-trends"),
  atmosphereForm: document.querySelector("#atmosphere-form"),
  atmosphereFormError: document.querySelector("#atmosphere-form-error"),
  atmosphereSubmitButton: document.querySelector("#atmosphere-submit-button"),
};

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);
}

function formatDate(value, options = { month: "short", day: "numeric" }) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown";
  return new Intl.DateTimeFormat(undefined, options).format(date);
}

function formatObservedAt(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function showPageError(message) {
  elements.alert.textContent = message;
  elements.alert.hidden = false;
}

function clearPageError() {
  elements.alert.textContent = "";
  elements.alert.hidden = true;
}

function statusLabel(level) {
  return {
    informational: "Informational",
    review: "Needs review",
    attention: "Attention",
  }[level] || "Unclassified";
}

function getVisibleObservations() {
  const search = elements.search.value.trim().toLowerCase();
  const status = elements.statusFilter.value;

  return state.observations.filter((observation) => {
    const category = CATEGORY_LABELS[observation.algae_type] || observation.algae_type;
    const matchesSearch = !search
      || observation.site_id.toLowerCase().includes(search)
      || category.toLowerCase().includes(search);
    const matchesStatus = status === "all" || observation.assessment_level === status;
    return matchesSearch && matchesStatus;
  });
}

function renderRows() {
  const visible = getVisibleObservations();
  if (visible.length === 0) {
    const hasFilters = elements.search.value.trim() || elements.statusFilter.value !== "all";
    elements.rows.innerHTML = `<tr><td class="table-message" colspan="5">${
      hasFilters ? "No observations match these filters." : "No observations yet. Add a field record to get started."
    }</td></tr>`;
    elements.observationCount.textContent = hasFilters
      ? "No matching records"
      : "No records saved yet";
    return;
  }

  elements.rows.innerHTML = visible.map((observation) => {
    const category = CATEGORY_LABELS[observation.algae_type] || observation.algae_type;
    const confidence = Math.round(observation.confidence * 100);
    const notes = observation.notes
      ? `<span>${escapeHtml(observation.notes)}</span>`
      : `<span>Observation record</span>`;
    return `
      <tr>
        <td><div class="site-cell"><strong>${escapeHtml(observation.site_id)}</strong>${notes}</div></td>
        <td class="category-cell">${escapeHtml(category)}</td>
        <td class="confidence-cell">
          <span class="confidence-label">${confidence}%</span>
          <span class="confidence-track"><span style="width:${confidence}%"></span></span>
        </td>
        <td><span class="status-badge status-${escapeHtml(observation.assessment_level)}">${escapeHtml(statusLabel(observation.assessment_level))}</span></td>
        <td class="date-cell">${escapeHtml(formatObservedAt(observation.observed_at))}</td>
      </tr>`;
  }).join("");

  elements.observationCount.textContent = `Showing ${visible.length} of ${state.observations.length} recent records`;
}

function renderBreakdown() {
  const counts = Object.fromEntries(Object.keys(CATEGORY_LABELS).map((key) => [key, 0]));
  for (const observation of state.observations) {
    if (Object.hasOwn(counts, observation.algae_type)) counts[observation.algae_type] += 1;
  }

  const maxCount = Math.max(1, ...Object.values(counts));
  elements.categoryBreakdown.innerHTML = Object.entries(CATEGORY_LABELS).map(([category, label]) => {
    const count = counts[category];
    const width = count === 0 ? 0 : Math.max(5, (count / maxCount) * 100);
    return `
      <div class="category-row">
        <span class="category-row-label">${escapeHtml(label)}</span>
        <span class="category-row-count">${count}</span>
        <span class="category-progress" data-category="${category}"><span style="width:${width}%"></span></span>
      </div>`;
  }).join("");
}

function renderSummary() {
  const reviewCount = state.observations.filter((item) => item.assessment_level === "review").length;
  const attentionCount = state.observations.filter((item) => item.assessment_level === "attention").length;
  const latest = state.observations[0];
  elements.total.textContent = state.observations.length;
  elements.review.textContent = reviewCount;
  elements.attention.textContent = attentionCount;
  elements.latest.textContent = latest ? formatDate(latest.observed_at) : "—";
}

function render() {
  renderSummary();
  renderRows();
  renderBreakdown();
}

function formatDuration(minutes) {
  if (minutes === null || minutes === undefined) return "—";
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
}

function renderAtmospherePriority(status) {
  const alert = status.highest_priority_alert;
  if (!alert) {
    elements.priorityAlert.hidden = true;
    elements.priorityAlert.replaceChildren();
    return;
  }

  elements.priorityAlert.innerHTML = `
    <strong>ATMOSPHERE ${escapeHtml(alert.level.toUpperCase())} — PRIORITY</strong>
    <span>${escapeHtml(alert.label)}: ${escapeHtml(alert.threshold)}. Air alerts take precedence over algae review items.</span>`;
  elements.priorityAlert.dataset.level = alert.level;
  elements.priorityAlert.hidden = false;
}

function renderAtmosphereAlerts(status) {
  const alerts = status.alerts || [];
  if (alerts.length === 0) {
    elements.atmosphereAlertContent.dataset.level = "";
    if (!status.reading) {
      elements.atmosphereAlertContent.innerHTML = `
        <span class="all-clear-mark" aria-hidden="true">—</span>
        <div><h2>Awaiting first sample</h2><p>No air threshold evaluation is available yet.</p></div>`;
      elements.atmosphereAlertList.innerHTML = '<p class="trend-empty">Submit a sample before interpreting air status.</p>';
      return;
    }
    elements.atmosphereAlertContent.innerHTML = `
      <span class="all-clear-mark" aria-hidden="true">✓</span>
      <div><h2>No threshold alerts</h2><p>The latest submitted sample is within the selected phase bands.</p></div>`;
    elements.atmosphereAlertList.innerHTML = '<p class="trend-empty">No threshold alerts for the latest sample.</p>';
    return;
  }

  const highest = status.highest_priority_alert || alerts[0];
  elements.atmosphereAlertContent.dataset.level = highest.level;
  elements.atmosphereAlertContent.innerHTML = `
    <span class="all-clear-mark" aria-hidden="true">${highest.level === "alarm" ? "!" : "△"}</span>
    <div>
      <h2>${escapeHtml(highest.level === "alarm" ? "Air alarm — highest priority" : "Air warning")}</h2>
      <p>${escapeHtml(highest.label)} is ${escapeHtml(highest.level)} at ${escapeHtml(highest.value)} ${escapeHtml(highest.unit)} (threshold ${escapeHtml(highest.threshold)}).</p>
    </div>`;
  elements.atmosphereAlertList.innerHTML = alerts.map((alert) => `
    <div class="air-alert-row" data-level="${escapeHtml(alert.level)}">
      <span class="air-alert-level">${escapeHtml(alert.level.toUpperCase())}</span>
      <span class="air-alert-main"><strong>${escapeHtml(alert.label)}</strong><small>Threshold ${escapeHtml(alert.threshold)} ${escapeHtml(alert.unit)}</small></span>
      <span class="air-alert-value">${escapeHtml(alert.value)} ${escapeHtml(alert.unit)}</span>
    </div>`).join("");
}

function renderAtmosphereTrends(trends) {
  if (!trends || trends.length === 0) {
    elements.atmosphereTrends.innerHTML = '<p class="trend-empty">Add at least two readings to see a direction estimate.</p>';
    return;
  }

  elements.atmosphereTrends.innerHTML = trends.map((trend) => `
    <div class="trend-card">
      <span>${escapeHtml(trend.label)}</span>
      <strong>${escapeHtml(trend.predicted_value)} ${escapeHtml(trend.unit)}</strong>
      <small class="trend-direction" data-direction="${escapeHtml(trend.direction)}">${escapeHtml(trend.direction)} in 30 min</small>
    </div>`).join("");
}

function renderAtmosphereStatus(status) {
  const modeNames = {
    steady: "Steady",
    acclimation: "Acclimation",
    co2_rise_alert: "CO₂ rapid rise alert",
    oxygen_depletion: "Oxygen depletion",
    contaminant_accumulation: "Contaminant accumulation",
    sensor_fault: "Sensor / circulation fault",
  };
  const mode = status.mode;
  const feedLabels = {
    online_manual: "Manual feed · online",
    stale: "Manual feed · stale",
    device_fault: "Device fault reported",
    awaiting_first_reading: "Waiting for first sample",
  };

  elements.atmosphereFeedPill.dataset.status = status.feed_status;
  elements.atmosphereFeedLabel.textContent = feedLabels[status.feed_status] || status.feed_status;
  elements.atmosphereMode.textContent = mode ? modeNames[mode] : "Awaiting reading";
  elements.atmosphereModeIndicator.dataset.mode = mode || "";
  elements.atmosphereModeDetail.textContent = mode === "sensor_fault"
    ? "Manual feed is stale or a sensor/circulation fault was reported."
    : mode
      ? "Displayed phase is operator-selected; minute-scale pattern recognition is unavailable."
      : "Submit a manual sample to begin monitoring.";
  elements.atmospherePhase.textContent = status.phase
    ? (status.phase === "steady" ? "Steady" : "Acclimation")
    : "—";
  elements.atmosphereDuration.textContent = formatDuration(status.mode_duration_minutes);
  elements.atmosphereConfidence.textContent = status.mode_confidence === null
    ? "Unavailable"
    : `${Math.round(status.mode_confidence * 100)}%`;
  elements.atmosphereSampledAt.textContent = status.sampled_at
    ? `Sampled ${formatObservedAt(status.sampled_at)}`
    : "No sample yet";
  document.querySelector("#threshold-phase-copy").textContent = status.phase
    ? `Using ${status.phase} phase thresholds.`
    : "No phase selected yet.";

  const reading = status.reading;
  document.querySelectorAll("[data-reading]").forEach((valueElement) => {
    const value = reading?.[valueElement.dataset.reading];
    valueElement.textContent = value === undefined || value === null ? "—" : value;
  });

  renderAtmosphereAlerts(status);
  renderAtmosphereTrends(status.trends);
  renderAtmospherePriority(status);
}

async function loadAtmosphereStatus() {
  try {
    const response = await fetch("/api/v1/atmosphere-cycle/status");
    if (!response.ok) throw new Error(`Could not load atmosphere status (HTTP ${response.status}).`);
    const status = await response.json();
    renderAtmosphereStatus(status);
  } catch (error) {
    elements.atmosphereFeedPill.dataset.status = "device_fault";
    elements.atmosphereFeedLabel.textContent = "Atmosphere API unavailable";
    elements.priorityAlert.innerHTML = `<strong>ATMOSPHERE DATA UNAVAILABLE — PRIORITY</strong><span>${escapeHtml(error.message)} Air status cannot be verified.</span>`;
    elements.priorityAlert.dataset.level = "alarm";
    elements.priorityAlert.hidden = false;
    elements.atmosphereMode.textContent = "Status unavailable";
    elements.atmosphereModeDetail.textContent = "The API did not return current atmosphere status.";
    elements.atmospherePhase.textContent = "—";
    elements.atmosphereDuration.textContent = "—";
    elements.atmosphereConfidence.textContent = "Unavailable";
    elements.atmosphereSampledAt.textContent = "Status unavailable";
    document.querySelectorAll("[data-reading]").forEach((valueElement) => {
      valueElement.textContent = "—";
    });
    elements.atmosphereAlertContent.dataset.level = "alarm";
    elements.atmosphereAlertContent.innerHTML = `
      <span class="all-clear-mark" aria-hidden="true">!</span>
      <div><h2>Air status cannot be verified</h2><p>Atmosphere service is unavailable. Do not treat stale readings as current.</p></div>`;
    elements.atmosphereAlertList.innerHTML = '<p class="trend-empty">No current threshold evaluation is available.</p>';
    elements.atmosphereTrends.innerHTML = '<p class="trend-empty">Trends are unavailable because the current status could not be loaded.</p>';
  }
}

async function loadObservations() {
  elements.systemState.textContent = "Checking";
  try {
    const response = await fetch("/api/v1/monitor/observations?limit=100");
    if (!response.ok) throw new Error(`Could not load observations (HTTP ${response.status}).`);
    const observations = await response.json();
    if (!Array.isArray(observations)) throw new Error("The monitor returned an unexpected response.");

    state.observations = observations;
    elements.systemState.textContent = "Online";
    clearPageError();
    render();
  } catch (error) {
    elements.systemState.textContent = "Offline";
    showPageError(`${error.message} Check the API connection and refresh.`);
    elements.rows.innerHTML = '<tr><td class="table-message error-message" colspan="5">Monitor data is unavailable.</td></tr>';
    elements.observationCount.textContent = "Unable to load records";
    elements.total.textContent = "—";
    elements.review.textContent = "—";
    elements.attention.textContent = "—";
    elements.latest.textContent = "—";
    elements.categoryBreakdown.innerHTML = '<div class="breakdown-empty">Category totals are unavailable while the API is offline.</div>';
  }
}

function setActiveView(viewName) {
  const isAtmosphere = viewName === "atmosphere";
  elements.overviewView.hidden = isAtmosphere;
  elements.atmosphereView.hidden = !isAtmosphere;
  elements.breadcrumb.textContent = isAtmosphere ? "Atmosphere Cycle" : "Overview";
  elements.navItems.forEach((item) => {
    const isActive = item.dataset.view === viewName;
    item.classList.toggle("active", isActive);
    if (isActive) item.setAttribute("aria-current", "page");
    else item.removeAttribute("aria-current");
  });
  if (isAtmosphere) loadAtmosphereStatus();
}

function openDialog() {
  elements.formError.hidden = true;
  elements.formError.textContent = "";
  elements.dialog.showModal();
}

function closeDialog() {
  elements.dialog.close();
}

async function submitObservation(event) {
  event.preventDefault();
  elements.formError.hidden = true;
  elements.formError.textContent = "";
  elements.submitButton.disabled = true;
  elements.submitButton.textContent = "Saving...";

  const formData = new FormData(elements.form);
  const payload = {
    site_id: formData.get("site_id").trim(),
    algae_type: formData.get("algae_type"),
    confidence: Number(formData.get("confidence")) / 100,
    notes: formData.get("notes").trim() || null,
  };

  try {
    const response = await fetch("/api/v1/monitor/observations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) {
      const detail = Array.isArray(result.detail)
        ? result.detail.map((item) => item.msg).join("; ")
        : result.detail;
      throw new Error(detail || `Could not save observation (HTTP ${response.status}).`);
    }

    elements.form.reset();
    elements.confidenceInput.value = "80";
    elements.confidenceValue.textContent = "80%";
    closeDialog();
    await loadObservations();
  } catch (error) {
    elements.formError.textContent = error.message || "Could not save this observation.";
    elements.formError.hidden = false;
  } finally {
    elements.submitButton.disabled = false;
    elements.submitButton.textContent = "Save observation";
  }
}

async function submitAtmosphereReading(event) {
  event.preventDefault();
  elements.atmosphereFormError.hidden = true;
  elements.atmosphereFormError.textContent = "";
  elements.atmosphereSubmitButton.disabled = true;
  elements.atmosphereSubmitButton.textContent = "Saving...";

  const formData = new FormData(elements.atmosphereForm);
  const payload = {
    site_id: formData.get("site_id").trim(),
    phase: formData.get("phase"),
    co2_ppm: Number(formData.get("co2_ppm")),
    o2_percent: Number(formData.get("o2_percent")),
    co_ppm: Number(formData.get("co_ppm")),
    temperature_c: Number(formData.get("temperature_c")),
    humidity_percent: Number(formData.get("humidity_percent")),
    pm25_ug_m3: Number(formData.get("pm25_ug_m3")),
    pm10_ug_m3: Number(formData.get("pm10_ug_m3")),
    tvoc_ppb: Number(formData.get("tvoc_ppb")),
    sensors_ok: formData.get("sensors_ok") === "true",
    circulation_running: formData.get("circulation_running") === "true",
  };

  try {
    const response = await fetch("/api/v1/atmosphere-cycle/readings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) {
      const detail = Array.isArray(result.detail)
        ? result.detail.map((item) => item.msg).join("; ")
        : result.detail;
      throw new Error(detail || `Could not save reading (HTTP ${response.status}).`);
    }

    elements.atmosphereForm.reset();
    await loadAtmosphereStatus();
  } catch (error) {
    elements.atmosphereFormError.textContent = error.message || "Could not save this reading.";
    elements.atmosphereFormError.hidden = false;
  } finally {
    elements.atmosphereSubmitButton.disabled = false;
    elements.atmosphereSubmitButton.textContent = "Save sample";
  }
}

document.querySelector("#today-label").textContent = new Intl.DateTimeFormat(undefined, {
  weekday: "short",
  month: "short",
  day: "numeric",
}).format(new Date());

document.querySelector("#new-observation-button").addEventListener("click", openDialog);
document.querySelector("#dialog-close").addEventListener("click", closeDialog);
document.querySelector("#cancel-button").addEventListener("click", closeDialog);
document.querySelector("#refresh-button").addEventListener("click", loadObservations);
elements.form.addEventListener("submit", submitObservation);
elements.search.addEventListener("input", renderRows);
elements.statusFilter.addEventListener("change", renderRows);
elements.confidenceInput.addEventListener("input", () => {
  elements.confidenceValue.textContent = `${elements.confidenceInput.value}%`;
});
elements.dialog.addEventListener("click", (event) => {
  if (event.target === elements.dialog) closeDialog();
});
elements.navItems.forEach((item) => {
  item.addEventListener("click", () => setActiveView(item.dataset.view));
});
document.querySelector("#atmosphere-refresh-button").addEventListener("click", loadAtmosphereStatus);
elements.atmosphereForm.addEventListener("submit", submitAtmosphereReading);

loadObservations();
loadAtmosphereStatus();
window.setInterval(loadAtmosphereStatus, 60_000);
