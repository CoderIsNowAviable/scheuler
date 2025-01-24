// Select DOM elements
const uploadBox = document.querySelector(".upload-box");
const uploadText = document.querySelector(".upload-text");
const selectButton = uploadBox.querySelector("button");

// Handle file selection via button
selectButton.addEventListener("click", () => {
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = "image/*";
    fileInput.multiple = true; // Allow multiple file selection
    fileInput.addEventListener("change", (event) => {
        handleBulkFileUpload(event.target.files);
    });
    fileInput.click();
});

// Handle drag-and-drop events
uploadBox.addEventListener("dragover", (event) => {
    event.preventDefault();
    uploadBox.classList.add("drag-over");
});

uploadBox.addEventListener("dragleave", () => {
    uploadBox.classList.remove("drag-over");
});

uploadBox.addEventListener("drop", (event) => {
    event.preventDefault();
    uploadBox.classList.remove("drag-over");
    const files = Array.from(event.dataTransfer.files);
    if (files.length > 0) handleBulkFileUpload(files);
});

// Function to handle bulk file upload
function handleBulkFileUpload(files) {
    const validFiles = Array.from(files).filter(file => file.type.startsWith("image/"));

    if (validFiles.length === 0) {
        alert("Please upload valid image files.");
        return;
    }

    // Clear previous previews
    uploadBox.innerHTML = "";

    // Display each uploaded image
    validFiles.forEach((file) => {
        const reader = new FileReader();
        reader.onload = () => {
            const imgWrapper = document.createElement("div");
            imgWrapper.classList.add("img-wrapper");

            const img = document.createElement("img");
            img.src = reader.result;
            img.alt = file.name;
            img.classList.add("uploaded-img");

            const imgName = document.createElement("p");
            imgName.textContent = file.name;

            imgWrapper.appendChild(img);
            imgWrapper.appendChild(imgName);
            uploadBox.appendChild(imgWrapper);
        };
        reader.readAsDataURL(file);
    });

    uploadBox.style.border = "none";
}


document.addEventListener("DOMContentLoaded", () => {
    // Fetch user details from the backend API
    fetch("/api/user")
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to fetch user data.");
            }
            return response.json();
        })
        .then((user) => {
            // Update the profile card with user data
            const profileName = document.querySelector(".profile-name");
            const profileEmail = document.querySelector(".profile-email");
            const profileImg = document.querySelector(".profile-img");

            profileName.textContent = user.name || "Anonymous";
            profileEmail.textContent = user.email || "Anonymous@example.com";
            if (user.profilePicture) {
                profileImg.src = user.profilePicture;
            }
        })
        .catch((error) => {
            console.error("Error loading user data:", error);
        });
    
    
    // Handle profile menu toggle
    const profileToggle = document.querySelector(".profile-toggle");
    const profileMenu = document.querySelector(".profile-options");

    profileToggle.addEventListener("click", () => {
        profileMenu.classList.toggle("visible");
    });

// Hide the dropdown with an animation when the mouse leaves
    profileMenu.addEventListener("mouseleave", () => {
        profileMenu.style.animation = "slideUp 0.3s ease"; // Play the slide-up animation
            setTimeout(() => {
    profileMenu.classList.remove("visible"); // Remove the visible class after the animation
        profileMenu.style.animation = ""; // Reset the animation style
    }, 300); // Match the duration of the slideUp animation
  });

    // Handle logout
    const logoutButton = document.getElementById("logout-button");
    logoutButton.addEventListener("click", () => {
        fetch("/api/logout", { method: "POST" })
            .then((response) => {
                if (response.ok) {
                    // Redirect to login page
                    window.location.href = "/";
                } else {
                    console.error("Logout failed.");
                }
            });
    });

    // Help link (can be routed to a help page)
    const helpLink = document.getElementById("help-link");
    helpLink.addEventListener("click", () => {
        alert("Redirecting to Help...");
    });
});
