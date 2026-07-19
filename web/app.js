const taskForm = document.querySelector("#task-form");
const taskList = document.querySelector("#task-list");
const statusFilter = document.querySelector("#status-filter");
const cardTemplate = document.querySelector("#task-card-template");
const loginForm = document.querySelector("#login-form");
const logoutButton = document.querySelector("#logout-button");
const authStatus = document.querySelector("#auth-status");

// All API calls are routed through the Nginx reverse proxy so the frontend stays origin-safe.
const API_BASE = "/api";
const TOKEN_STORAGE_KEY = "taskboard.token";

function getToken() {
  // Pulls the saved token from browser storage.
  // Input: None.
  // Output: Returns the stored token string or null.
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

function setToken(token) {
  // Saves the active token in browser storage.
  // Input: One token string.
  // Output: Keeps the token ready for later requests.
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

function clearToken() {
  // Removes the saved token from browser storage.
  // Input: None.
  // Output: Clears the stored token.
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

function updateAuthStatus(message, isError = false) {
  // Updates the login status text in the page.
  // Input: A message string and an optional error flag.
  // Output: Changes the status label in the UI.
  authStatus.textContent = message;
  authStatus.style.color = isError ? "#b42318" : "#36554f";
}

async function apiRequest(path, options = {}) {
  // Sends an authenticated request to the API.
  // Input: An API path and fetch options.
  // Output: Returns parsed JSON, null for no content, or throws an error.
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
  // Logs the user in and stores the returned token.
  // Input: A username and password string.
  // Output: Saves the token and updates the auth status text.
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
  // Formats a due date for display in the task card.
  // Input: A raw date string or a missing value.
  // Output: Returns a human-readable date label.
  if (!raw) {
    return "No due date";
  }

  const parsed = new Date(raw);
  return Number.isNaN(parsed.getTime()) ? "Invalid date" : parsed.toLocaleDateString();
}

function renderTaskCard(task) {
  // Builds one task card and wires its actions.
  // Input: One task object from the API.
  // Output: Returns a DOM fragment ready to append to the list.
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

  // Saves the new status when the dropdown changes.
  // Input: The selected status value from the card.
  // Output: The task is updated, then the list is refreshed.
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

  // Deletes the task after the user confirms the action.
  // Input: A click on the delete button.
  // Output: The card is removed, or an error alert appears.
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
  // Shows the empty-state message in the task list.
  // Input: None.
  // Output: Replaces the list with one empty-state element.
  taskList.innerHTML = "";
  const empty = document.createElement("div");
  empty.className = "empty-state";
  empty.textContent = "No tasks match this view yet.";
  taskList.appendChild(empty);
}

async function refreshTasks() {
  // Reloads tasks from the API and redraws the list.
  // Input: The current status filter from the page.
  // Output: Updates the task list with matching tasks.
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

// Handles login submissions and reloads the list after success.
// Input: A form submit event with username and password values.
// Output: Saves a token, updates the page, or shows an error.
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

// Handles logout clicks and clears the current session state.
// Input: A click on the logout button.
// Output: The saved token is cleared and the empty state returns.
logoutButton.addEventListener("click", () => {
  clearToken();
  updateAuthStatus("Logged out.");
  renderEmptyState();
});

// Handles new task submissions and refreshes the board.
// Input: A form submit event with task details.
// Output: Creates a task, resets the form, and redraws the list.
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

// Refreshes the board when the status filter changes.
// Input: A filter selection change.
// Output: The task list is reloaded for the new filter.
statusFilter.addEventListener("change", () => {
  refreshTasks().catch((error) => alert(error.message));
});

if (getToken()) {
  // Restores the saved session on page load.
  // Input: A token already stored in browser storage.
  // Output: The auth label and task list are restored.
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
