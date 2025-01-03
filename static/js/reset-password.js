document.getElementById("reset-password-form").addEventListener("submit", function(event) {
    event.preventDefault();  // Prevent form submission

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
        alert("Invalid reset link.");
        return;
    }

    // Send password reset request to backend
    fetch("/users/reset-password", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ token: resetToken, new_password: password }),
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.message === "Password reset successful!") {
            alert("Your password has been reset. You can now log in.");
            window.location.href = "/signin.html";  // Redirect to login page
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch((error) => {
        alert("Error resetting password: " + error.message);
    });
});
