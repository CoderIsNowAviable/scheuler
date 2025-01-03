document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const email = urlParams.get("email");
  const token = urlParams.get("token");

  if (email && token) {
    localStorage.setItem("email", email);
    localStorage.setItem("token", token);
  }

  const inputs = document.querySelectorAll(".code-box");
  const submitButton = document.querySelector(".submit-btn");
  const emailField = document.getElementById("emailField");
  const tokenField = document.getElementById("tokenField");

  emailField.value = email || "";
  tokenField.value = token || "";

  inputs.forEach((input, index) => {
    input.addEventListener("input", (e) => {
      if (!/^\d$/.test(e.target.value)) {
        e.target.value = "";
        return;
      }
      if (index < inputs.length - 1 && e.target.value) {
        inputs[index + 1].focus();
      }
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Backspace") {
        if (e.target.value) {
          e.target.value = "";
        } else if (index > 0) {
          inputs[index - 1].focus();
        }
        e.preventDefault();
      }

      if (e.key === "ArrowLeft" && index > 0) {
        inputs[index - 1].focus();
      }

      if (e.key === "ArrowRight" && index < inputs.length - 1) {
        inputs[index + 1].focus();
      }
    });
  });

  submitButton.addEventListener("click", () => {
    const email = emailField.value;
    const token = tokenField.value;
    const verificationCode = Array.from(inputs).map((input) => input.value).join("");

    if (!email) {
      alert("Email is missing. Please log in again.");
      return;
    }

    if (verificationCode.length !== 5) {
      alert("Please enter a valid 5-digit code.");
      return;
    }

    fetch("/users/verify-code", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ email, verification_code: verificationCode }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message === "Verification successful!") {
          window.location.href = "/dashboard";
        } else {
          alert("Error verifying code: " + data.detail);
        }
      })
      .catch((error) => {
        alert("Error verifying code: " + error.message);
      });
  });

  document.getElementById("resend-code-btn").addEventListener("click", () => {
    const email = localStorage.getItem("email");

    if (!email) {
      alert("Email not found. Please try signing in again.");
      return;
    }

    fetch("/users/resend-verification-code", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",  // This ensures the server knows it's JSON
      },
      body: JSON.stringify({ user_email: email }),  // Correct request body
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error("Failed to resend verification code");
        }
      })
      .then((data) => {
        alert(data.message || "New verification code has been sent to your email.");
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred while resending the verification code.");
      });
  });
});
