document.addEventListener("DOMContentLoaded", () => {
    const inputs = document.querySelectorAll(".code-box");
    const submitButton = document.querySelector(".submit-btn");
    const emailField = document.getElementById("emailField");
    const tokenField = document.getElementById("tokenField");
  
    // Combine the input boxes logic
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
  
    // Handle Submit Button
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
  
        // Send the verification data to the server
        fetch("/users/verify-code", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                email: email.trim(),
                verification_code: verificationCode.trim(),
            }),
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.message === "Verification successful!") {
                window.location.href = "/dashboard"; // Redirect on success
            } else {
                alert("Error verifying code: " + data.detail);
            }
        })
        .catch((error) => {
            alert("Error verifying code: " + error.message);
        });
    });
  
    // Resend verification code
    document.querySelector(".resend").addEventListener("click", () => {
        const email = emailField.value;
        const token = tokenField.value;
  
        // Make sure token exists
        if (!token) {
            alert("You are not logged in.");
            return;
        }
  
        // Send request to resend verification code
        fetch("/users/resend-code", { 
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ email: email.trim() }), 
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === "Verification code resent successfully!") {
                alert("Verification code resent successfully. Check your email!");
            } else {
                alert("Error: " + data.detail);
            }
        })
        .catch(error => {
            alert("An error occurred: " + error.message);
        });
    });
  });