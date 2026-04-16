(function () {
  const API_BASE_URL = window.API_BASE_URL || "http://localhost:8000";

  const form = document.getElementById("entry-form");
  const entryIdInput = document.getElementById("entry-id");
  const saveButton = document.getElementById("save-button");
  const cancelEditButton = document.getElementById("cancel-edit-button");
  const formMessage = document.getElementById("form-message");

  const filterDateFrom = document.getElementById("filter-date-from");
  const filterDateTo = document.getElementById("filter-date-to");
  const filterPerson = document.getElementById("filter-person");
  const filterTeam = document.getElementById("filter-team");
  const applyFiltersButton = document.getElementById("apply-filters");
  const clearFiltersButton = document.getElementById("clear-filters");

  const tableBody = document.getElementById("entries-body");
  const tableMessage = document.getElementById("table-message");

  let currentEntries = [];

  function setFormMode(mode) {
    if (mode === "create") {
      entryIdInput.value = "";
      saveButton.textContent = "Save entry";
      cancelEditButton.classList.add("hidden");
    } else {
      saveButton.textContent = "Update entry";
      cancelEditButton.classList.remove("hidden");
    }
  }

  function showFormMessage(text, type) {
    formMessage.textContent = text;
    formMessage.classList.remove("error", "success");
    if (type) {
      formMessage.classList.add(type);
    }
  }

  function showTableMessage(text, type) {
    tableMessage.textContent = text;
    tableMessage.classList.remove("error", "success");
    if (type) {
      tableMessage.classList.add(type);
    }
  }

  function buildQueryParams() {
    const params = new URLSearchParams();
    if (filterDateFrom.value) params.append("date_from", filterDateFrom.value);
    if (filterDateTo.value) params.append("date_to", filterDateTo.value);
    if (filterPerson.value.trim()) params.append("person_name", filterPerson.value.trim());
    if (filterTeam.value.trim()) params.append("team", filterTeam.value.trim());
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  }

  async function fetchEntries() {
    showTableMessage("Loading entries...", "");
    tableBody.innerHTML = "";
    try {
      const response = await fetch(`${API_BASE_URL}/api/time-entries${buildQueryParams()}`);
      if (!response.ok) {
        throw new Error(`Failed to load entries (HTTP ${response.status})`);
      }
      const data = await response.json();
      currentEntries = Array.isArray(data) ? data : [];
      renderEntries();
      if (currentEntries.length === 0) {
        showTableMessage("No entries found for the selected filters.", "");
      } else {
        showTableMessage(`Showing ${currentEntries.length} entr${currentEntries.length === 1 ? "y" : "ies"}.`, "");
      }
    } catch (err) {
      console.error(err);
      showTableMessage(`Error loading entries: ${err.message}`, "error");
    }
  }

  function renderEntries() {
    tableBody.innerHTML = "";
    currentEntries.forEach((entry) => {
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td>${escapeHtml(entry.date)}</td>
        <td>${escapeHtml(entry.person_name)}</td>
        <td>${escapeHtml(entry.team)}</td>
        <td>${escapeHtml(entry.activity)}</td>
        <td>${escapeHtml(entry.start_time)}</td>
        <td>${escapeHtml(entry.end_time)}</td>
        <td>${entry.duration_minutes != null ? escapeHtml(String(entry.duration_minutes)) : ""}</td>
        <td>
          <div class="actions">
            <button type="button" data-action="edit" data-id="${entry.id}">Edit</button>
            <button type="button" class="danger" data-action="delete" data-id="${entry.id}">Delete</button>
          </div>
        </td>
      `;

      tableBody.appendChild(tr);
    });
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function getFormPayload() {
    const date = form.date.value;
    const person_name = form.person_name.value.trim();
    const team = form.team.value.trim();
    const activity = form.activity.value.trim();
    const start_time = form.start_time.value;
    const end_time = form.end_time.value;
    const durationRaw = form.duration_minutes.value;

    const payload = { date, person_name, team, activity, start_time, end_time };
    if (durationRaw !== "") {
      payload.duration_minutes = Number(durationRaw);
    }
    return payload;
  }

  async function createEntry(payload) {
    const response = await fetch(`${API_BASE_URL}/api/time-entries`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Create failed (HTTP ${response.status}): ${text || ""}`);
    }
    return response.json();
  }

  async function updateEntry(id, payload) {
    const response = await fetch(`${API_BASE_URL}/api/time-entries/${encodeURIComponent(id)}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Update failed (HTTP ${response.status}): ${text || ""}`);
    }
    return response.json();
  }

  async function deleteEntry(id) {
    const response = await fetch(`${API_BASE_URL}/api/time-entries/${encodeURIComponent(id)}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Delete failed (HTTP ${response.status}): ${text || ""}`);
    }
  }

  function resetForm() {
    form.reset();
    setFormMode("create");
    showFormMessage("", "");
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    showFormMessage("Saving...", "");
    saveButton.disabled = true;

    const id = entryIdInput.value;
    const payload = getFormPayload();

    try {
      if (id) {
        const original = currentEntries.find((e) => e.id === id) || {};
        const patchPayload = {};
        Object.keys(payload).forEach((key) => {
          if (payload[key] !== "" && payload[key] !== original[key]) {
            patchPayload[key] = payload[key];
          }
        });
        if (Object.keys(patchPayload).length === 0) {
          showFormMessage("No changes to save.", "");
        } else {
          await updateEntry(id, patchPayload);
          showFormMessage("Entry updated.", "success");
        }
      } else {
        await createEntry(payload);
        showFormMessage("Entry created.", "success");
      }
      resetForm();
      await fetchEntries();
    } catch (err) {
      console.error(err);
      showFormMessage(err.message, "error");
    } finally {
      saveButton.disabled = false;
    }
  });

  cancelEditButton.addEventListener("click", () => {
    resetForm();
  });

  applyFiltersButton.addEventListener("click", () => {
    fetchEntries();
  });

  clearFiltersButton.addEventListener("click", () => {
    filterDateFrom.value = "";
    filterDateTo.value = "";
    filterPerson.value = "";
    filterTeam.value = "";
    fetchEntries();
  });

  tableBody.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;

    const id = button.getAttribute("data-id");
    const action = button.getAttribute("data-action");

    if (action === "edit") {
      const entry = currentEntries.find((e) => e.id === id);
      if (!entry) return;
      entryIdInput.value = entry.id;
      form.date.value = entry.date;
      form.person_name.value = entry.person_name;
      form.team.value = entry.team;
      form.activity.value = entry.activity;
      form.start_time.value = entry.start_time;
      form.end_time.value = entry.end_time;
      form.duration_minutes.value = entry.duration_minutes != null ? entry.duration_minutes : "";
      setFormMode("edit");
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else if (action === "delete") {
      if (!confirm("Delete this entry? This cannot be undone.")) return;
      try {
        await deleteEntry(id);
        await fetchEntries();
      } catch (err) {
        console.error(err);
        alert(err.message);
      }
    }
  });

  document.addEventListener("DOMContentLoaded", () => {
    fetchEntries();
  });
})();
