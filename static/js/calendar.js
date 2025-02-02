export function initializeCalendar() {
  const calendarEl = document.getElementById("calendar");

  if (calendarEl && typeof FullCalendar !== "undefined") {
    const calendar = new FullCalendar.Calendar(calendarEl, {
      schedulerLicenseKey: "GPL-My-Project-Is-Open-Source",
      initialView: "dayGridMonth", // Default view
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
      eventContent: function (arg) {
        let mediaUrl = arg.event.extendedProps.media; // Get media URL
        let title = arg.event.title;
      
        console.log("Media URL: ", mediaUrl); // Log to debug
        let decodedMediaUrl = decodeURIComponent(mediaUrl);
        console.log("Decoded Media URL: ", decodedMediaUrl); // Log to debug
        let innerHtml = "";

        if (mediaUrl) {
          innerHtml += `<img src="${decodedMediaUrl}" alt="Event Image" style="width: 50px; margin-right: 5px;">`;
        }

        innerHtml += `<span>${title}</span>`;

        return { html: innerHtml };
      },
    });

    // Render the calendar
    calendar.render();

    console.log("Calendar initialized with view dropdown");
  } else {
    console.error(
      "FullCalendar is not defined or #calendar element is missing"
    );
  }
}
