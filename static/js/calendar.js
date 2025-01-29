export function initializeCalendar() {
  const calendarEl = document.getElementById("calendar");

  if (calendarEl && typeof FullCalendar !== "undefined") {
    const calendar = new FullCalendar.Calendar(calendarEl, {
      schedulerLicenseKey: "GPL-My-Project-Is-Open-Source",
      initialView: "timeGridWeek", // Default view
      height: "auto",
      scrollTime: "21:00:00", // Default scroll to 9 PM
      headerToolbar: {
        left: "title", // Keep navigation buttons
        center: "", // Keep the title in the center
        right: "dayGridMonth,timeGridWeek,timeGridDay, prev,today,next", // Remove default view buttons
      },
      events: async function (fetchInfo, successCallback, failureCallback) {
        try {
          const response = await fetch("/dashboard/api/events");
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

    // Add dropdown functionality
    const dropdownBtn = document.getElementById("dropdown-btn");
    const dropdownMenu = document.getElementById("dropdown-menu");

    dropdownBtn.addEventListener("click", () => {
      dropdownMenu.classList.toggle("hidden");
    });

    dropdownMenu.addEventListener("click", (event) => {
      const view = event.target.getAttribute("data-view");
      if (view) {
        calendar.changeView(view); // Change the calendar view
        dropdownMenu.classList.add("hidden");
      }
    });

    console.log("Calendar initialized with view dropdown");
  } else {
    console.error(
      "FullCalendar is not defined or #calendar element is missing"
    );
  }
}
