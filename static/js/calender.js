document.addEventListener("DOMContentLoaded", function () {
    function initializeCalendar() {
      const calendarEl = document.getElementById("calendar");
      if (calendarEl && typeof FullCalendar !== "undefined") {
        const calendar = new FullCalendar.Calendar(calendarEl, {
          schedulerLicenseKey: "GPL-My-Project-Is-Open-Source",
          initialView: "timeGridWeek", // Default to weekly scrollable view
          height: "auto", // Adjust height dynamically
          scrollTime: "09:00:00", // Scroll to 9 AM by default
          headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek,timeGridDay",
          },
          events: [
            {
              id: "1",
              resourceId: "a",
              title: "Meeting",
              start: "2025-01-25T10:00:00",
              end: "2025-01-25T12:00:00",
            },
          ],
        });
        calendar.render();
      } else {
        console.error(
          "FullCalendar is not defined or calendar element is missing"
        );
      }
    }
  
    // Call the initializeCalendar function after DOMContentLoaded
    initializeCalendar();
  });
  