document.addEventListener("DOMContentLoaded", function () {
  const profileToggle = document.querySelector(".profile-toggle");
  const profileMenu = document.querySelector(".profile-options");
  const switchProfileBtn = document.getElementById("switch-profile-btn");
  const profilePhotoInput = document.getElementById("profile-photo-input");
  const profileImg = document.querySelector(".profile-img");
  const profileEmail = document.getElementById("profile-email")?.value;
  const links = document.querySelectorAll("a[data-link]");
  const mainContent = document.getElementById("main-content");
  const formData = new FormData();
  const file = profilePhotoInput?.files[0];

  // Profile menu toggle
  profileToggle?.addEventListener("click", () => {
    profileMenu?.classList.toggle("visible");
  });

  // Switch Profile button click - triggers file input
  switchProfileBtn?.addEventListener("click", () => {
    profilePhotoInput?.click(); // Trigger the hidden file input
  });

  // Handle file input change (when a user selects a file)
  profilePhotoInput?.addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const email = profileEmail;
    const formData = new FormData();
    if (file) {
      formData.append("profile_photo", file);
      formData.append("email", email);
    }

    // Send the request to upload the profile photo
    try {
      const response = await fetch("/upload-profile-photo", {
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

  // Function to load sections dynamically
  async function loadSection(section) {
    console.log(`Loading section: ${section}`);
    if (!mainContent) {
      console.error("Main content element is missing!");
      return;
    }

    // Update active link
    links.forEach((link) => link.classList.remove("active"));
    const activeLink = document.querySelector(`a[data-link="${section}"]`);
    activeLink?.classList.add("active");

    try {
      const response = await fetch(`/dashboard/${section}`);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const html = await response.text();
      mainContent.innerHTML = html;
      console.log(`Loaded content for section: ${section}`);

      // Dynamically import section-specific JS
      if (section === "schedule") {
        const { initializeSchedule } = await import(`/static/js/schedule.js`);
        initializeSchedule();
      } else if (section === "calendar") {
        initializeCalendar(); // Initialize calendar directly
      }
    } catch (error) {
      console.error("Error loading section:", error);
      mainContent.innerHTML = `<p>Error loading section: ${section}</p>`;
    }
  }

  // Function to initialize the calendar
  function initializeCalendar() {
    const calendarEl = document.getElementById("calendar");
    if (calendarEl && typeof FullCalendar !== "undefined") {
      const calendar = new FullCalendar.Calendar(calendarEl, {
        schedulerLicenseKey: "GPL-My-Project-Is-Open-Source",
        initialView: "timeGridWeek",
        height: "auto",
        scrollTime: "09:00:00",
        headerToolbar: {
          left: "prev,next today",
          center: "title",
          right: "dayGridMonth,timeGridWeek,timeGridDay",
        },
        events: "/api/events", // Replace with your dynamic API endpoint
      });
      calendar.render();
      console.log("Calendar initialized");
    } else {
      console.error("FullCalendar is not defined or #calendar element is missing");
    }
  }

  // Initial load
  loadSection("schedule");

  // Navigation
  links.forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      const section = link.getAttribute("data-link");
      loadSection(section);
    });
  });
});
