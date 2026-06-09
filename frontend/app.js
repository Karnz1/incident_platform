const API_BASE = 'http://localhost:8000';
const incidentForm = document.getElementById('incidentForm');
const titleInput = document.getElementById('titleInput');
const descriptionInput = document.getElementById('descriptionInput');
const incidentListEl = document.getElementById('incidentList');
const incidentCountEl = document.getElementById('incidentCount');
const toastEl = document.getElementById('toast');

let incidents = [];
let refreshIntervalId = null;
console.log('test')
function showToast(message, type = 'info') {
  toastEl.textContent = message;
  toastEl.className = `toast visible`;
  if (type === 'error') {
    toastEl.style.borderColor = 'rgba(245, 138, 138, 0.45)';
  } else {
    toastEl.style.borderColor = 'rgba(92, 123, 255, 0.25)';
  }

  clearTimeout(showToast.timeoutId);
  showToast.timeoutId = setTimeout(() => {
    toastEl.className = 'toast hidden';
  }, 3200);
}

function updateIncidentCount() {
  incidentCountEl.textContent = incidents.length;
}

function formatDateTime(value) {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleString();
}

function renderIncidents() {
  incidentListEl.innerHTML = '';

  if (!incidents.length) {
    incidentListEl.innerHTML = `
      <div class="empty-state">
        <h3>No incidents yet</h3>
        <p>Create your first incident using the form above.</p>
      </div>
    `;
    updateIncidentCount();
    return;
  }

  incidents.forEach((incident) => {
    const card = document.createElement('article');
    card.className = 'incident-card';
    card.innerHTML = `
      <div class="card-meta">
        <div>
          <h3>${escapeHtml(incident.title)}</h3>
          <div class="meta-row">
            <span class="meta-pill">Status: ${escapeHtml(incident.status || '—')}</span>
            <span class="meta-pill" style="border-color: ${incident.severity_color || 'rgba(92, 123, 255, 0.25)'}; color: ${incident.severity_color || '#5c7bff'}">Severity: ${escapeHtml(incident.severity ?? '—')}</span>
            <span class="meta-pill">SLA: ${escapeHtml(formatDateTime(incident.sla_deadline))}</span>
          </div>
        </div>
        <button class="delete-btn" data-id="${incident.id}">Delete</button>
      </div>
      <p>${escapeHtml(incident.description)}</p>
    `;

    const deleteButton = card.querySelector('.delete-btn');
    deleteButton.addEventListener('click', () => deleteIncident(incident.id));
    incidentListEl.appendChild(card);
  });

  updateIncidentCount();
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

async function fetchIncidents() {
  try {
    const response = await fetch(`${API_BASE}/incidents`);

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }

    incidents = await response.json();
    renderIncidents();
  } catch (error) {
    showToast('Unable to load incidents from backend.', 'error');
    console.error('Fetch incidents error:', error);
  }
}

async function createIncident(title, description) {
  try {
    const response = await fetch(`${API_BASE}/incidents`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title, description }),
    });

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }

    await response.json();
    await fetchIncidents();
    showToast('Incident queued successfully.');
    return true;
  } catch (error) {
    showToast('Unable to create incident. Check backend connection.', 'error');
    console.error('Create incident error:', error);
    return false;
  }
}

async function deleteIncident(id) {
  try {
    const response = await fetch(`${API_BASE}/incidents/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }

    await fetchIncidents();
    showToast('Incident deleted.');
  } catch (error) {
    showToast('Delete failed. Verify backend availability.', 'error');
    console.error('Delete incident error:', error);
  }
}

incidentForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const title = titleInput.value.trim();
  const description = descriptionInput.value.trim();

  if (!title || !description) {
    showToast('Please add both title and description.', 'error');
    return;
  }

  const created = await createIncident(title, description);
  if (created) {
    titleInput.value = '';
    descriptionInput.value = '';
  }
});

fetchIncidents();
refreshIntervalId = setInterval(fetchIncidents, 5000);
