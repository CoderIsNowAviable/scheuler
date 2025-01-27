document.addEventListener("DOMContentLoaded", function () {
  const profileToggle = document.querySelector(".profile-toggle");
  const profileMenu = document.querySelector(".profile-options");
  const switchProfileBtn = document.getElementById("switch-profile-btn");
  const profilePhotoInput = document.getElementById("profile-photo-input");
  const profileImg = document.querySelector(".profile-img");
  const profileEmail = document.getElementById("profile-email")?.value;
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

      const email = profileEmail;
      const formData = new FormData();
      formData.append("profile_photo", file);
      formData.append("email", email);

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
  }

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
    if (activeLink) {
      activeLink.classList.add("active");
    }

    try {
      // Log request URL for debugging
      console.log(`Fetching content for: /dashboard/${section}`);
      const response = await fetch(`/dashboard/${section}`);

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const html = await response.text();
      console.log("Fetched HTML:", html); // Log the fetched HTML content

      mainContent.innerHTML = html;
      console.log(`Loaded content for section: ${section}`);

      // Initialize section-specific JS
      if (section === "schedule") {
        const { initializeSchedule } = await import(`/static/js/schedule.js`);
        initializeSchedule();
      } else if (section === "calendar") {
        initializeCalendar(); // Initialize calendar directly
      }
    } catch (error) {
      console.error("Error loading section:", error);
      mainContent.innerHTML = `<p>Error loading section: ${section}. Please try again later.</p>`;
    }
  }

  function initializeSchedule() {
    console.log("Schedule section initialized");
    // Add specific logic for the schedule section here
  }

  function initializeCalendar() {
    const calendarEl = document.getElementById("calendar");
  
    if (calendarEl && typeof FullCalendar !== "undefined") {
      const calendar = new FullCalendar.Calendar(calendarEl, {
        schedulerLicenseKey: "GPL-My-Project-Is-Open-Source",
        initialView: "timeGridWeek", // Default view
        height: "auto",
        scrollTime: "21:00:00", // Default scroll to 9 PM
        headerToolbar: {
          left: "prev,next today", // Keep navigation buttons
          center: "title", // Keep the title in the center
          right: "", // Remove default view buttons
        },
        events: async function (fetchInfo, successCallback, failureCallback) {
          try {
            const response = await fetch("/api/events");
            const data = await response.json();
  
            // Map events properly
            const events = data.map((event) => ({
              title: event.title,
              start: event.start || event.end,
              end: event.end,
              extendedProps: {
                description: event.description,
                tags: event.tags,
                file_location: event.file_location,
              },
            }));
  
            successCallback(events);
          } catch (error) {
            console.error("Failed to fetch events:", error);
            failureCallback(error);
          }
        },
      });
  
      // Render the calendar
      calendar.render();
  
      // Add a custom dropdown for switching views
      const dropdown = document.createElement("select");
      dropdown.id = "view-switcher";
      dropdown.innerHTML = `
        <option value="dayGridMonth">Month</option>
        <option value="timeGridWeek">Week</option>
        <option value="timeGridDay">Day</option>
      `;
      dropdown.addEventListener("change", function () {
        const selectedView = this.value;
        calendar.changeView(selectedView); // Switch the calendar view
      });
  
      // Append the dropdown to the toolbar
      const toolbarCenter = calendarEl.querySelector(".fc-toolbar-chunk:nth-child(2)");
      if (toolbarCenter) {
        toolbarCenter.appendChild(dropdown);
      }
  
      console.log("Calendar initialized with view dropdown");
    } else {
      console.error("FullCalendar is not defined or #calendar element is missing");
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
});
