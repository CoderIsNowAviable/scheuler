document.addEventListener("DOMContentLoaded", function () {
  const profileToggle = document.querySelector(".profile-toggle");
  const profileMenu = document.querySelector(".profile-options");
  const switchProfileBtn = document.getElementById("switch-profile-btn");
  const profilePhotoInput = document.getElementById("profile-photo-input");
  const profileImg = document.querySelector(".profile-img");
  const profileEmail = document.getElementById("profile-email");
  const links = document.querySelectorAll("a[data-link]");
  const mainContent = document.getElementById("main-content");

  // Profile menu toggle
  if (profileToggle && profileMenu) {
    profileToggle.addEventListener("click", () => {
      profileMenu.classList.toggle("visible");
    });
  }

  // Switch Profile button click - triggers file input
  if (switchProfileBtn && profilePhotoInput) {
    switchProfileBtn.addEventListener("click", () => {
      profilePhotoInput.click(); // Trigger the hidden file input
    });
  }

  // Handle file input change (when a user selects a file)
  if (profilePhotoInput) {
    profilePhotoInput.addEventListener("change", async (event) => {
      const file = event.target.files[0];
      if (!file) return;

      const email = profileEmail?.value || window.userData.email; // Use the global user data for email
      const formData = new FormData();
      formData.append("profile_photo", file);
      formData.append("email", email);

      // Send the request to upload the profile photo
      try {
        const response = await fetch("/dashboard/upload-profile-photo", {
          method: "POST",
          body: formData,
        });
        const result = await response.json();
        if (result.success) {
          // Update the profile image on the page
          profileImg.src = result.newPhotoUrl;
          alert("Profile photo updated successfully!");
        } else {
          alert("Failed to upload profile photo.");
        }
      } catch (error) {
        console.error("Error uploading profile photo:", error);
        alert("Error uploading profile photo.");
      }
    });
  }

  // Function to load sections dynamically
  async function loadSection(section) {
    console.log(`Loading section: ${section}`);
    if (!mainContent) {
      console.error("Main content element is missing!");
      return;
    }

    links.forEach((link) => link.classList.remove("active"));
    const activeLink = document.querySelector(`a[data-link="${section}"]`);
    if (activeLink) {
      activeLink.classList.add("active");
    }

    try {
      console.log(`Fetching content for: /dashboard/me/${section}`);
      const response = await fetch(`/dashboard/me/${section}`, {
        method: "GET",
        credentials: "include", // Ensures cookies/session are sent
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const html = await response.text();
      console.log("Fetched HTML:", html);

      mainContent.innerHTML = html;
      console.log(`Loaded content for section: ${section}`);

      if (section === "schedule") {
        const { initializeSchedule } = await import(`/static/js/schedule.js`);
        initializeSchedule();
      } else if (section === "calendar") {
        const { initializeCalendar } = await import(`/static/js/calendar.js`);
        initializeCalendar();
      }
    } catch (error) {
      console.error("Error loading section:", error);
      mainContent.innerHTML = `<p>Error loading section: ${section}. Please try again later.</p>`;
    }
  }

  // Get the active page from localStorage on page load
  const activePage = localStorage.getItem("activePage");

  // If there's an active page stored, load that section, otherwise default to 'schedule'
  if (activePage && (activePage === "schedule" || activePage === "calendar")) {
    loadSection(activePage); // Load the saved section
  } else {
    loadSection("schedule"); // Default to "schedule" if no section is saved
  }

  // Navigation
  links.forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      const section = link.getAttribute("data-link");
      loadSection(section);
      // Store the active section in localStorage
      localStorage.setItem("activePage", section);
    });
  });

  // Update profile photo on page load using global user data
  if (profileImg) {
    profileImg.src =
      window.userData.profilePhotoUrl || "default_profile_photo_url.png"; // Use global profile photo URL
  }

  // Optional: Show TikTok username and profile picture if available
  const tiktokUsernameElement = document.querySelector(".tiktok-username");
  const tiktokProfilePicElement = document.querySelector(".tiktok-profile-pic");

  if (tiktokUsernameElement) {
    tiktokUsernameElement.textContent =
      window.userData.tiktokUsername || "Not connected to TikTok";
  }

  if (tiktokProfilePicElement) {
    tiktokProfilePicElement.src =
      window.userData.tiktokProfilePicture || "default_tiktok_profile_pic.png";
  }
});
