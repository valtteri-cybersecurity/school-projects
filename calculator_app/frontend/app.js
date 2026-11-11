"use strict";

// Samassa originissa käytetään suhteellista polkua. AWS-julkaisussa
// vaihda tähän API Gatewayn HTTPS-osoite (esim. https://...execute-api...amazonaws.com).
const API_BASE_URL = "";

const form = document.querySelector("#calculator-form");
const resultElement = document.querySelector("#result");
const messageElement = document.querySelector("#message");
const calculateButton = document.querySelector("#calculate-button");

function showMessage(text, isError = false) {
  messageElement.textContent = text;
  messageElement.classList.toggle("error", isError);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const aInput = document.querySelector("#number-a");
  const bInput = document.querySelector("#number-b");
  const operation = form.querySelector('input[name="operation"]:checked').value;
  const aText = aInput.value.trim();
  const bText = bInput.value.trim();

  if (aText === "" || bText === "") {
    showMessage("Anna molemmat luvut.", true);
    return;
  }

  const a = Number(aText);
  const b = Number(bText);
  if (!Number.isFinite(a) || !Number.isFinite(b)) {
    showMessage("Anna kelvolliset luvut.", true);
    return;
  }
  if (operation === "divide" && b === 0) {
    showMessage("Nollalla ei voi jakaa.", true);
    return;
  }

  calculateButton.disabled = true;
  resultElement.textContent = "…";
  showMessage("Lasketaan…");

  try {
    const response = await fetch(`${API_BASE_URL}/calculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ a, b, operation }),
    });

    const data = await response.json();
    if (!response.ok) {
      const detail = typeof data.detail === "string"
        ? data.detail
        : "Tarkista syötteet ja yritä uudelleen.";
      throw new Error(detail);
    }
    if (typeof data.result !== "number" || !Number.isFinite(data.result)) {
      throw new Error("Palvelin palautti virheellisen tuloksen.");
    }

    resultElement.textContent = String(data.result);
    showMessage("Laskutoimitus onnistui.");
  } catch (error) {
    resultElement.textContent = "—";
    showMessage(error instanceof TypeError
      ? "API-palvelimeen ei saatu yhteyttä."
      : error.message, true);
  } finally {
    calculateButton.disabled = false;
  }
});

form.addEventListener("reset", () => {
  resultElement.textContent = "—";
  showMessage("Anna luvut ja paina Laske tulos.");
});
