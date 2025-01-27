export function initializeCalendar() {
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
  