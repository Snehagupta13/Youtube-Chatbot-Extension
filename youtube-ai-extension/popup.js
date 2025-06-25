document.addEventListener("DOMContentLoaded", async () => {
  const chatModeBtn = document.getElementById("chatModeBtn");
  const summarizeModeBtn = document.getElementById("summarizeModeBtn");
  const chatContainer = document.getElementById("chatContainer");
  const summarizeContainer = document.getElementById("summarizeContainer");
  const askBtn = document.getElementById("askBtn");
  const summarizeBtn = document.getElementById("summarizeBtn");
  const questionInput = document.getElementById("question");
  const responseBox = document.getElementById("response");
  const videoIdElement = document.getElementById("videoId");

  let currentVideoId = null;
  let currentMode = 'chat'; // 'chat' or 'summarize'

  // Check if we're on a YouTube video page
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const url = new URL(tab.url);
    
    if (url.hostname.includes("youtube.com") && url.searchParams.get("v")) {
      currentVideoId = url.searchParams.get("v");
      videoIdElement.textContent = currentVideoId;
    } else {
      showError("Please open a YouTube video first.");
      disableAllButtons();
    }
  } catch (error) {
    showError("Error detecting YouTube video.");
    disableAllButtons();
  }

  // Mode switching
  chatModeBtn.addEventListener("click", () => switchMode('chat'));
  summarizeModeBtn.addEventListener("click", () => switchMode('summarize'));

  // Button actions
  askBtn.addEventListener("click", handleQuestion);
  summarizeBtn.addEventListener("click", handleSummarize);
  questionInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleQuestion();
    }
  });

  function switchMode(mode) {
    currentMode = mode;
    if (mode === 'chat') {
      chatModeBtn.classList.add("active");
      summarizeModeBtn.classList.remove("active");
      chatContainer.style.display = "block";
      summarizeContainer.style.display = "none";
    } else {
      chatModeBtn.classList.remove("active");
      summarizeModeBtn.classList.add("active");
      chatContainer.style.display = "none";
      summarizeContainer.style.display = "block";
    }
    clearResponse();
  }

  function disableAllButtons() {
    askBtn.disabled = true;
    summarizeBtn.disabled = true;
    chatModeBtn.disabled = true;
    summarizeModeBtn.disabled = true;
  }

  function showLoading() {
    responseBox.innerHTML = '<div class="loader"></div>';
  }

  function showError(message) {
    responseBox.innerHTML = `<div class="error">${message}</div>`;
  }

  function clearResponse() {
    responseBox.textContent = '';
  }

  async function callAPI(endpoint, data) {
    try {
      showLoading();
      const response = await fetch(`http://localhost:8000/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...data, video_id: currentVideoId })
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const result = await response.json();
      responseBox.textContent = result.answer || "No response received";
    } catch (error) {
      console.error("API Error:", error);
      showError(error.message.includes("No transcript") ? 
        "This video has no captions available." : 
        "Error processing your request. Please try again.");
    }
  }

  async function handleQuestion() {
    const question = questionInput.value.trim();
    if (!question) {
      showError("Please enter a question.");
      return;
    }
    if (!currentVideoId) {
      showError("No YouTube video detected.");
      return;
    }
    await callAPI("ask", { question });
  }

  async function handleSummarize() {
    if (!currentVideoId) {
      showError("No YouTube video detected.");
      return;
    }
    await callAPI("summarize", {});
  }
});