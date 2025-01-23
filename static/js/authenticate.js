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
          inputs[index - 1].value = "";
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
    const verificationCode = Array.from(inputs)
      .map((input) => input.value)
      .join("");

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
      body: JSON.stringify({
        email: email.trim(),
        verification_code: verificationCode.trim(),
      }),
    })
      .then((response) => {
        // Log the response content-type and status
        console.log("Response status:", response.status);
        console.log(
          "Response Content-Type:",
          response.headers.get("Content-Type")
        );

        // Check if the response is not JSON (e.g., it's HTML)
        if (response.headers.get("Content-Type").includes("text/html")) {
          throw new Error("Received HTML instead of JSON.");
        }

        if (!response.ok) {
          return response.json().then((data) => {
            throw new Error(data.detail || "An error occurred");
          });
        }

        return response.json(); // Parse JSON response
      })
      .then((data) => {
        // Check if verification was successful
        if (data.message === "Verification successful!") {
          // Redirect to the dashboard with the token in the URL
          window.location.href = `/dashboard?token=${data.access_token}`;
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
        "Content-Type": "application/json", // This ensures the server knows it's JSON
      },
      body: JSON.stringify({ user_email: email }), // Correct request body
    })
      .then((response) => response.json())
      .then((data) => {
        // Log or display the server message
        if (data.message === "Verification code is still valid.") {
          alert("Verification code is still valid.");
        } else if (data.message === "Verification code resent successfully") {
          alert("A new verification code has been sent to your email.");
        } else {
          alert("An unexpected response was received.");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred while resending the verification code.");
      });
  });
});
