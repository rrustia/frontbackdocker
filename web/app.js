const taskForm = document.querySelector("#task-form");
const taskList = document.querySelector("#task-list");
const statusFilter = document.querySelector("#status-filter");
const cardTemplate = document.querySelector("#task-card-template");
const loginForm = document.querySelector("#login-form");
const logoutButton = document.querySelector("#logout-button");
const authStatus = document.querySelector("#auth-status");

// I route all API calls through the Nginx reverse proxy so frontend stays origin-safe.
const API_BASE = "/api";
const TOKEN_STORAGE_KEY = "taskboard.token";

function getToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

function updateAuthStatus(message, isError = false) {
  authStatus.textContent = message;
  authStatus.style.color = isError ? "#b42318" : "#36554f";
}

async function apiRequest(path, options = {}) {
  const token = getToken();
  const authHeader = token ? { Authorization: `Bearer ${token}` } : {};

  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...authHeader,
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`API request failed (${response.status}): ${body}`);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

async function login(username, password) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Login failed (${response.status}): ${body}`);
  }

  const data = await response.json();
  setToken(data.access_token);
  updateAuthStatus(`Authenticated as ${username}.`);
}

function formatDate(raw) {
  if (!raw) {
    return "No due date";
  }

  const parsed = new Date(raw);
  return Number.isNaN(parsed.getTime()) ? "Invalid date" : parsed.toLocaleDateString();
}

function renderTaskCard(task) {
  const fragment = cardTemplate.content.cloneNode(true);

  const card = fragment.querySelector(".task-card");
  const title = fragment.querySelector(".task-title");
  const description = fragment.querySelector(".task-description");
  const meta = fragment.querySelector(".task-meta");
  const statusSelect = fragment.querySelector(".status-select");
  const deleteButton = fragment.querySelector(".delete-button");

  title.textContent = task.title;
  description.textContent = task.description || "No description provided.";
  meta.textContent = `Priority: ${task.priority} | Due: ${formatDate(task.due_date)}`;
  statusSelect.value = task.status;

  statusSelect.addEventListener("change", async () => {
    try {
      await apiRequest(`/tasks/${task.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: statusSelect.value }),
      });
      await refreshTasks();
    } catch (error) {
      alert(error.message);
    }
  });

  deleteButton.addEventListener("click", async () => {
    const approved = confirm(`Delete task "${task.title}"?`);
    if (!approved) {
      return;
    }

    try {
      await apiRequest(`/tasks/${task.id}`, { method: "DELETE" });
      card.remove();
      if (!taskList.children.length) {
        renderEmptyState();
      }
    } catch (error) {
      alert(error.message);
    }
  });

  return fragment;
}

function renderEmptyState() {
  taskList.innerHTML = "";
  const empty = document.createElement("div");
  empty.className = "empty-state";
  empty.textContent = "No tasks match this view yet.";
  taskList.appendChild(empty);
}

async function refreshTasks() {
  const params = new URLSearchParams();
  if (statusFilter.value) {
    params.set("status", statusFilter.value);
  }

  const path = params.toString() ? `/tasks?${params}` : "/tasks";
  const tasks = await apiRequest(path);

  taskList.innerHTML = "";
  if (!tasks.length) {
    renderEmptyState();
    return;
  }

  for (const task of tasks) {
    taskList.appendChild(renderTaskCard(task));
  }
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(loginForm);
  const username = String(formData.get("username") || "").trim();
  const password = String(formData.get("password") || "");

  try {
    await login(username, password);
    await refreshTasks();
  } catch (error) {
    updateAuthStatus(error.message, true);
  }
});

logoutButton.addEventListener("click", () => {
  clearToken();
  updateAuthStatus("Logged out.");
  renderEmptyState();
});

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(taskForm);
  const payload = {
    title: formData.get("title"),
    description: formData.get("description") || null,
    priority: formData.get("priority"),
    due_date: formData.get("due_date") || null,
  };

  try {
    await apiRequest("/tasks", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    taskForm.reset();
    await refreshTasks();
  } catch (error) {
    alert(error.message);
  }
});

statusFilter.addEventListener("change", () => {
  refreshTasks().catch((error) => alert(error.message));
});

if (getToken()) {
  updateAuthStatus("Authenticated using saved token.");
  refreshTasks().catch((error) => {
    taskList.innerHTML = "";
    const issue = document.createElement("div");
    issue.className = "empty-state";
    issue.textContent = `Unable to load tasks: ${error.message}`;
    taskList.appendChild(issue);
  });
} else {
  renderEmptyState();
}
