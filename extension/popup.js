const API_BASE = "http://localhost:8000";

const urlTextEl = document.getElementById("url-text");
const statusCardEl = document.getElementById("status-card");
const statusChipEl = document.getElementById("status-chip");
const statusHeadlineEl = document.getElementById("status-headline");
const statusSubtitleEl = document.getElementById("status-subtitle");
const riskFillEl = document.getElementById("risk-fill");
const scanButtonEl = document.getElementById("scan-button");
const rescanButtonEl = document.getElementById("rescan-button");

function setNeutralState() {
  statusCardEl.classList.remove("safe", "phishing");
  statusChipEl.textContent = "Ready to scan";
  statusHeadlineEl.textContent = "One tap to know if this page is safe.";
  statusSubtitleEl.textContent =
    "We run a local AI model over the URL structure — nothing leaves your machine.";
  riskFillEl.style.width = "100%";
}

function setLoadingState() {
  statusCardEl.classList.remove("safe", "phishing");
  statusChipEl.textContent = "Analyzing…";
  statusHeadlineEl.textContent = "Running structural checks on the URL.";
  statusSubtitleEl.textContent = "This usually takes less than a second.";
}

function setErrorState(message) {
  statusCardEl.classList.remove("safe");
  statusCardEl.classList.add("phishing");
  statusChipEl.textContent = "Error";
  statusHeadlineEl.textContent = "We couldn’t reach the local scanner.";
  statusSubtitleEl.textContent =
    message ||
    "Ensure the phishing detection API is running on http://localhost:8000.";
  riskFillEl.style.width = "0%";
}

function applyResult(isPhishing, probability) {
  const pct = Math.round(probability * 100);
  riskFillEl.style.width = `${100 - pct}%`;

  if (isPhishing) {
    statusCardEl.classList.remove("safe");
    statusCardEl.classList.add("phishing");
    statusChipEl.textContent = "High risk";
    statusHeadlineEl.textContent = "This URL looks dangerous.";
    statusSubtitleEl.textContent = `Our model assigns a phishing probability of ${pct}%. Proceed only if you fully trust the source.`;
  } else {
    statusCardEl.classList.remove("phishing");
    statusCardEl.classList.add("safe");
    statusChipEl.textContent = "Likely safe";
    statusHeadlineEl.textContent = "This URL appears legitimate.";
    statusSubtitleEl.textContent = `Our model assigns a phishing probability of ${pct}%. Still stay cautious with unknown sites.`;
  }
}

async function getActiveTabUrl() {
  return new Promise((resolve) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      resolve(tab ? tab.url : "");
    });
  });
}

async function scanCurrentUrl() {
  const url = await getActiveTabUrl();
  if (!url) {
    urlTextEl.textContent = "No active tab URL found.";
    setErrorState("Open a page in a tab and try again.");
    return;
  }

  urlTextEl.textContent = url;
  setLoadingState();

  try {
    const response = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url })
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || `HTTP ${response.status}`);
    }

    const data = await response.json();
    applyResult(data.is_phishing, data.probability_phishing);
    rescanButtonEl.classList.remove("hidden");
  } catch (err) {
    console.error("Prediction error", err);
    setErrorState(err.message);
  }
}

scanButtonEl.addEventListener("click", () => {
  scanCurrentUrl();
});

rescanButtonEl.addEventListener("click", () => {
  setNeutralState();
  scanCurrentUrl();
});

// Initialize
(async function init() {
  setNeutralState();
  const url = await getActiveTabUrl();
  urlTextEl.textContent = url || "Waiting for active tab URL…";
})();


