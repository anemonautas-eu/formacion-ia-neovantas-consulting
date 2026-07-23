const sentence = ["El", "banco", "está", "junto", "al", "río"];

const attentionPatterns = {
  El: {
    weights: [0.46, 0.34, 0.08, 0.04, 0.03, 0.05],
    interpretation: "“El” queda ligado al sustantivo que determina",
  },
  banco: {
    weights: [0.06, 0.16, 0.04, 0.09, 0.05, 0.6],
    interpretation: "“banco” se interpreta como orilla",
  },
  está: {
    weights: [0.05, 0.29, 0.2, 0.22, 0.08, 0.16],
    interpretation: "“está” conecta la entidad con su localización",
  },
  junto: {
    weights: [0.02, 0.17, 0.2, 0.2, 0.15, 0.26],
    interpretation: "“junto” construye una relación espacial",
  },
  al: {
    weights: [0.02, 0.1, 0.08, 0.22, 0.17, 0.41],
    interpretation: "“al” introduce el término de la relación",
  },
  río: {
    weights: [0.03, 0.47, 0.04, 0.16, 0.12, 0.18],
    interpretation: "“río” refuerza el sentido geográfico de “banco”",
  },
};

const tokenRow = document.querySelector("#token-row");
const weightBars = document.querySelector("#weight-bars");
const interpretation = document.querySelector("#interpretation");

function renderAttention(query) {
  const pattern = attentionPatterns[query];
  interpretation.textContent = pattern.interpretation;

  [...tokenRow.children].forEach((button, index) => {
    const weight = pattern.weights[index];
    button.classList.toggle("is-query", button.dataset.token === query);
    button.setAttribute("aria-pressed", button.dataset.token === query ? "true" : "false");
    button.dataset.weight = `${Math.round(weight * 100)}%`;
    const lightness = 96 - weight * 48;
    button.style.backgroundColor = `hsl(11 100% ${lightness}%)`;
    button.style.color = weight > 0.56 ? "white" : "#151716";
  });

  weightBars.innerHTML = sentence
    .map((token, index) => {
      const value = pattern.weights[index];
      return `
        <div class="weight-item">
          <span>${token}</span>
          <div class="weight-track"><div class="weight-fill" style="--weight: ${value * 100}%"></div></div>
          <span class="weight-value">${value.toFixed(2)}</span>
        </div>`;
    })
    .join("");
}

sentence.forEach((token) => {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "token";
  button.dataset.token = token;
  button.textContent = token;
  button.setAttribute("aria-label", `Consultar atención de ${token}`);
  button.addEventListener("click", () => renderAttention(token));
  tokenRow.append(button);
});

renderAttention("banco");

const quiz = document.querySelector(".quiz-card");
const quizFeedback = document.querySelector(".quiz-feedback");

quiz.querySelectorAll("button").forEach((button) => {
  button.addEventListener("click", () => {
    if (quiz.dataset.answered === "true") return;

    const isCorrect = button.dataset.correct === "true";
    quiz.dataset.answered = "true";
    button.classList.add(isCorrect ? "correct" : "incorrect");
    quizFeedback.textContent = isCorrect
      ? "Exacto. Esa conexión directa y el paralelismo son dos aportaciones centrales."
      : "No exactamente. La atención mejora las conexiones y el paralelismo, pero no elimina todos los costes ni implica comprensión humana.";

    quiz.querySelectorAll("button").forEach((option) => {
      option.disabled = true;
      if (option.dataset.correct === "true") option.classList.add("correct");
    });
  });
});

const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const reveals = document.querySelectorAll(".reveal");

if (prefersReducedMotion || !("IntersectionObserver" in window)) {
  reveals.forEach((element) => element.classList.add("is-visible"));
} else {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12 }
  );
  reveals.forEach((element) => observer.observe(element));
}
