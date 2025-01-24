document.addEventListener("DOMContentLoaded", () => {
  // Utility Functions
  const fetchUserData = () => {
    fetch("/api/user")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch user data.");
        }
        return response.json();
      })
      .then((user) => updateProfileCard(user))
      .catch((error) => console.error("Error loading user data:", error));
  };

  const updateProfileCard = (user) => {
    const profileName = document.querySelector(".profile-name");
    const profileEmail = document.querySelector(".profile-email");
    const profileImg = document.querySelector(".profile-img");

    profileName.textContent = user.name || "Anonymous";
    profileEmail.textContent = user.email || "Anonymous@example.com";
    if (user.profilePicture) {
      profileImg.src = user.profilePicture;
    }
  };

  const toggleDropdown = (dropdown, visibleClass, leaveAnimation) => {
    dropdown.classList.toggle(visibleClass);
    dropdown.addEventListener("mouseleave", () => {
      dropdown.style.animation = leaveAnimation;
      setTimeout(() => {
        dropdown.classList.remove(visibleClass);
        dropdown.style.animation = "";
      }, 300); // Match animation duration
    });
  };
  
  const handleProfilePhotoUpload = (file) => {
    const formData = new FormData();
    formData.append("profile_photo", file);

    fetch("/upload-profile-photo", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          const profileImg = document.getElementById("profile-img");
          profileImg.src = data.newPhotoUrl;
          alert("Profile photo updated successfully!");
        } else {
          alert("Error updating profile photo.");
        }
      })
      .catch((error) => {
        console.error("Error uploading photo:", error);
        alert("Error uploading photo.");
      });
  };

  const handleFileUpload = (files, uploadBox) => {
    const validFiles = Array.from(files).filter((file) =>
      file.type.startsWith("image/")
    );

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
  };

  // Handle Profile Menu Toggle
  const profileToggle = document.querySelector(".profile-toggle");
  const profileMenu = document.querySelector(".profile-options");

  profileToggle?.addEventListener("click", () => {
    toggleDropdown(profileMenu, "visible", "slideUp 0.3s ease");
  });

  // Handle Profile Photo Upload
  const switchProfileBtn = document.getElementById("switch-profile-btn");
  const profilePhotoInput = document.getElementById("profile-photo-input");

  switchProfileBtn?.addEventListener("click", () => {
    profilePhotoInput.click();
  });

  profilePhotoInput?.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (file) handleProfilePhotoUpload(file);
  });

  // Handle Logout
  const logoutButton = document.getElementById("logout-button");
  logoutButton?.addEventListener("click", () => {
    fetch("/api/logout", { method: "POST" })
      .then((response) => {
        if (response.ok) {
          window.location.href = "/";
        } else {
          console.error("Logout failed.");
        }
      })
      .catch((error) => console.error("Error logging out:", error));
  });

  // Handle Help Link
  const helpLink = document.getElementById("help-link");
  helpLink?.addEventListener("click", () => {
    alert("Redirecting to Help...");
  });

  // Handle Image Upload
  const uploadBox = document.querySelector(".upload-box");
  const selectButton = document.getElementById("select-photo-btn");

  // Drag-and-drop functionality
  uploadBox?.addEventListener("dragover", (event) => {
    event.preventDefault();
    uploadBox.classList.add("drag-over");
  });

  uploadBox?.addEventListener("dragleave", () => {
    uploadBox.classList.remove("drag-over");
  });

  uploadBox?.addEventListener("drop", (event) => {
    event.preventDefault();
    uploadBox.classList.remove("drag-over");
    handleFileUpload(event.dataTransfer.files, uploadBox);
  });

  // File selection via button click
  selectButton?.addEventListener("click", () => {
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = "image/*";
    fileInput.multiple = true;
    fileInput.addEventListener("change", (event) => {
      handleFileUpload(event.target.files, uploadBox);
    });
    fileInput.click();
  });

  // Handle Add TikTok Account
  const bindAccountBtn = document.getElementById("bind-account-btn");
  const addAccountCard = document.querySelector(".add-account");
  const boundAccountCard = document.querySelector(".bound-account");

  bindAccountBtn?.addEventListener("click", () => {
    addAccountCard.classList.add("hidden");
    boundAccountCard.classList.remove("hidden");
  });

  // Fetch and update user details on page load
  fetchUserData();
});
