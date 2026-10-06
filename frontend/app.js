const API_BASE = window.DOCMIND_API_URL || "http://127.0.0.1:8000";

const state = {
  documentId: null,
  filename: null,
  uploading: false,
  messages: [],
};

const $ = (selector) => document.querySelector(selector);
const emptyState = $("#empty-state");
const messages = $("#messages");
const question = $("#question");
const askButton = $("#ask-button");
const fileInput = $("#file-input");
const dropzone = $("#dropzone");
const documentCard = $("#document-card");
const uploadError = $("#upload-error");
const typing = $("#typing");
const sourcesList = $("#sources-list");
const apiStatus = $("#api-status");
const apiDot = $("#api-dot");

function setApiStatus(label, isError = false) {
  apiStatus.textContent = label;
  apiStatus.parentElement.classList.toggle("error", isError);
  apiDot.style.background = isError ? "#c86d5c" : "";
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.hidden = false;
  window.setTimeout(() => { toast.hidden = true; }, 3600);
}

function setUploadError(message = "") {
  uploadError.textContent = message;
  uploadError.hidden = !message;
}

function setDocumentReady(filename, chunks) {
  state.filename = filename;
  documentCard.hidden = false;
  dropzone.hidden = true;
  $("#document-name").textContent = filename;
  $("#document-status").textContent = `${chunks} chunks · ready to ask`;
  $("#file-count").textContent = "1 / 1";
  $("#upload-progress").style.width = "100%";
  question.disabled = false;
  askButton.disabled = false;
  setApiStatus("Document ready");
}

async function uploadDocument(file) {
  if (!file) return;
  if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
    setUploadError("Please choose a PDF file.");
    return;
  }
  state.uploading = true;
  setUploadError();
  $("#document-name").textContent = file.name;
  $("#document-status").textContent = "Extracting text and building index…";
  documentCard.hidden = false;
  dropzone.hidden = true;
  $("#upload-progress").style.width = "35%";
  setApiStatus("Processing document…");

  const formData = new FormData();
  formData.append("file", file);
  try {
    const response = await fetch(`${API_BASE}/documents/upload`, { method: "POST", body: formData });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok || payload.error) throw new Error(payload.detail || payload.error || "The document could not be processed.");
    state.documentId = payload.document_id;
    setDocumentReady(payload.filename || file.name, payload.chunks || 0);
    showToast("Your document is ready to explore.");
  } catch (error) {
    state.documentId = null;
    documentCard.hidden = true;
    dropzone.hidden = false;
    setUploadError(error.message.includes("Failed to fetch") ? "Could not reach the API. Start FastAPI on port 8000 and try again." : error.message);
    setApiStatus("API connection failed", true);
  } finally {
    state.uploading = false;
    fileInput.value = "";
  }
}

function renderMessage(role, content) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  if (role === "assistant") {
    const label = document.createElement("p");
    label.className = "message-label";
    label.textContent = "DocMind";
    bubble.append(label);
  }
  const text = document.createElement("div");
  text.textContent = content;
  bubble.append(text);
  wrapper.append(bubble);
  messages.append(wrapper);
}

function renderSources(sources = []) {
  sourcesList.replaceChildren();
  if (!sources.length) {
    sourcesList.innerHTML = '<div class="sources-empty">No source pages were returned for this answer.</div>';
    return;
  }
  sources.forEach((source) => {
    const card = document.createElement("div");
    card.className = "source-card";
    card.innerHTML = `<div class="source-page">P${source.page}</div><div class="source-copy"><strong>Page ${source.page}</strong><span>Match distance ${Number(source.distance).toFixed(2)}</span></div>`;
    sourcesList.append(card);
  });
}

async function askQuestion(text) {
  const trimmed = text.trim();
  if (!trimmed || !state.documentId || state.uploading) return;
  question.value = "";
  question.style.height = "auto";
  emptyState.hidden = true;
  messages.classList.add("has-messages");
  renderMessage("user", trimmed);
  typing.hidden = false;
  askButton.disabled = true;
  question.disabled = true;
  setApiStatus("Searching your document…");
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ document_id: state.documentId, question: trimmed }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok || payload.error) throw new Error(payload.detail || payload.error || "The answer could not be generated.");
    renderMessage("assistant", payload.answer || "I could not find an answer in the provided document.");
    renderSources(payload.sources);
    setApiStatus("Answer grounded in your document");
  } catch (error) {
    renderMessage("assistant", error.message.includes("Failed to fetch") ? "I could not reach the API. Check that FastAPI is running, then try again." : error.message);
    setApiStatus("API connection failed", true);
  } finally {
    typing.hidden = true;
    askButton.disabled = false;
    question.disabled = false;
    question.focus();
  }
}

function clearSession() {
  state.documentId = null;
  state.filename = null;
  state.messages = [];
  messages.replaceChildren();
  messages.classList.remove("has-messages");
  emptyState.hidden = false;
  documentCard.hidden = true;
  dropzone.hidden = false;
  question.value = "";
  question.disabled = true;
  askButton.disabled = true;
  sourcesList.innerHTML = '<div class="sources-empty">Sources will appear here after your first answer.</div>';
  $("#file-count").textContent = "0 / 1";
  setUploadError();
  setApiStatus("Ready to connect");
}

fileInput.addEventListener("change", () => uploadDocument(fileInput.files[0]));
["dragenter", "dragover"].forEach((eventName) => dropzone.addEventListener(eventName, (event) => { event.preventDefault(); dropzone.classList.add("dragging"); }));
["dragleave", "drop"].forEach((eventName) => dropzone.addEventListener(eventName, (event) => { event.preventDefault(); dropzone.classList.remove("dragging"); }));
dropzone.addEventListener("drop", (event) => uploadDocument(event.dataTransfer.files[0]));
$("#question-form").addEventListener("submit", (event) => { event.preventDefault(); askQuestion(question.value); });
question.addEventListener("input", () => { question.style.height = "auto"; question.style.height = `${Math.min(question.scrollHeight, 130)}px`; });
question.addEventListener("keydown", (event) => { if ((event.metaKey || event.ctrlKey) && event.key === "Enter") { event.preventDefault(); askQuestion(question.value); } });
$("#remove-document").addEventListener("click", clearSession);
$("#new-session").addEventListener("click", clearSession);
document.querySelectorAll(".suggestion").forEach((button) => button.addEventListener("click", () => {
  if (!state.documentId) { showToast("Upload a PDF first, then try this prompt."); return; }
  question.value = button.dataset.question;
  askQuestion(question.value);
}));
