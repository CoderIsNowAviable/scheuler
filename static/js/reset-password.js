document.getElementById("reset-password-form").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent form submission

    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirm-password");
    const passwordError = document.getElementById("password-error");
    const confirmPasswordError = document.getElementById("confirm-password-error");

    const password = passwordInput.value.trim();
    const confirmPassword = confirmPasswordInput.value.trim();

    // Clear previous error messages
    passwordError.textContent = "";
    confirmPasswordError.textContent = "";

    // Validate passwords
    if (password.length < 6) {
        passwordError.textContent = "Password must be at least 6 characters.";
        return;
    }

    if (password !== confirmPassword) {
        confirmPasswordError.textContent = "Passwords do not match.";
        return;
    }

    // Get the reset token from the URL
    const urlParams = new URLSearchParams(window.location.search);
    const resetToken = urlParams.get("token");

    if (!resetToken) {
        alert("Invalid or expired reset link.");
        return;
    }
    console.log("Sending data:", JSON.stringify({ token: resetToken, new_password: password }));

    // Send password reset request to backend
    fetch("/users/reset-password", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ token: resetToken, new_password: password }),
    })
        .then((response) => {
            if (!response.ok) {
                return response.json().then((data) => {
                    throw new Error(data.detail || "Error resetting password.");
                });
            }
            return response.json();
        })
        .then((data) => {
            alert("Your password has been reset successfully.");
            window.location.href = "/signin.html"; // Redirect to login page
        })
        .catch((error) => {
            alert("Error: " + error.message);
        });
});
