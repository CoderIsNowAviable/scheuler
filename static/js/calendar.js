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
              media: event.media_url, // Add media URL for the image
            },
          }));

          successCallback(events);
        } catch (error) {
          console.error("Failed to fetch events:", error);
          failureCallback(error);
        }
      },
      // Event rendering logic
      eventRender: function(info) {
        const eventElement = info.el;
        const mediaUrl = info.event.extendedProps.media; // Get media URL from extendedProps
        if (mediaUrl) {
          const imgElement = document.createElement("img");
          imgElement.src = mediaUrl;
          imgElement.alt = "Event Image";
          imgElement.style.width = "50px"; // Adjust the size as needed
          imgElement.style.marginRight = "5px"; // Space between image and title

          // Prepend the image to the event title
          const titleElement = eventElement.querySelector(".fc-event-title");
          titleElement.insertBefore(imgElement, titleElement.firstChild);
        }
      }
    });

    // Render the calendar
    calendar.render();

    console.log("Calendar initialized with view dropdown");
  } else {
    console.error("FullCalendar is not defined or #calendar element is missing");
  }
}
