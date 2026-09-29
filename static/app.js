const taskEl = document.getElementById("task");
const inputEl = document.getElementById("inputText");
const submitBtn = document.getElementById("submitBtn");
const statusEl = document.getElementById("status");
const resultCard = document.getElementById("resultCard");
const resultEl = document.getElementById("result");
const downloadBtn = document.getElementById("downloadBtn");

let latestResult = "";

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  }[ch]));
}

function showError(message) {
  resultCard.classList.remove("hidden");
  resultEl.textContent = message;
  resultEl.classList.add("error-result");
}

function clearErrorStyle() {
  resultEl.classList.remove("error-result");
}

function renderResult(task, data) {
  clearErrorStyle();

  if (task !== "quiz") {
    latestResult = String(data.result ?? "");
    resultEl.textContent = latestResult;
    return;
  }

  const quiz = data.result;

  if (!quiz || !Array.isArray(quiz.questions)) {
    throw new Error("The quiz response has an invalid format.");
  }

  if (quiz.questions.length !== 3) {
    throw new Error("The quiz response must contain exactly 3 questions.");
  }

  latestResult = JSON.stringify(quiz, null, 2);

  resultEl.innerHTML = quiz.questions.map((q, i) => {
    const options = Array.isArray(q.options) ? q.options : [];
    return `
      <article class="quiz-question">
        <h3>${i + 1}. ${escapeHtml(q.question || "Question")}</h3>
        ${options.map((option) => `<div class="option">${escapeHtml(option)}</div>`).join("")}
        <p class="correct">Correct answer: ${escapeHtml(q.correct_answer || "Not provided")}</p>
      </article>
    `;
  }).join("");
}

async function readApiResponse(response) {
  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `Request failed (${response.status})`);
    }

    return data;
  }

  // Defensive fallback for unexpected HTML/plain-text server responses.
  const text = await response.text();
  throw new Error(
    text?.trim() || `Server returned an unexpected response (${response.status}).`
  );
}

submitBtn.addEventListener("click", async () => {
  const task = taskEl.value;
  const text = inputEl.value.trim();

  if (!text) {
    statusEl.textContent = "Please enter a question, topic, or passage.";
    showError("Please enter a question, topic, or passage.");
    return;
  }

  submitBtn.disabled = true;
  statusEl.textContent = "EduGenie is thinking...";
  resultCard.classList.add("hidden");
  latestResult = "";

  try {
    const response = await fetch("/task", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task, text })
    });

    const data = await readApiResponse(response);
    renderResult(task, data);
    resultCard.classList.remove("hidden");
    statusEl.textContent = "Done.";
  } catch (error) {
    const message = error instanceof Error
      ? error.message
      : "Something went wrong.";

    statusEl.textContent = message;
    showError(message);
  } finally {
    submitBtn.disabled = false;
  }
});

downloadBtn.addEventListener("click", () => {
  if (!latestResult) return;

  const blob = new Blob([latestResult], {
    type: "text/plain;charset=utf-8"
  });

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "edugenie-result.txt";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
});
