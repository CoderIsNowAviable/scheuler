document.getElementById("forgot-password-form").addEventListener("submit", function(event) {
    event.preventDefault();  // Prevent form submission

    const emailInput = document.getElementById("email");
    const email = emailInput.value.trim();
    const emailError = document.getElementById("email-error");

    // Clear previous error messages
    emailError.textContent = "";

    // Validate email
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    if (!email) {
        emailError.textContent = "Email address is required.";
        return;
    }

    if (!emailRegex.test(email)) {
        emailError.textContent = "Please enter a valid email address.";
        return;
    }

    // Send reset request (This is where you'd integrate with your backend)
    fetch("/users/forgot-password-reset", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ email: email }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("A reset link has been sent to your email.");
            window.location.href = "/register?form=signin";  // Redirect to sign-in page
        } else {
            emailError.textContent = data.message || "Error sending reset link.";
        }
    })
    .catch(error => {
        emailError.textContent = "An error occurred. Please try again.";
    });
});
