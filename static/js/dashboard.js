// script.js

// Image Storage System
const uploadImageForm = document.getElementById('uploadImageForm');
const imageGallery = document.getElementById('imageGallery');

uploadImageForm.addEventListener('submit', (e) => {
  e.preventDefault();

  const imageFile = document.getElementById('imageFile').files[0];
  if (!imageFile) {
    alert('Please select an image to upload.');
    return;
  }

  const reader = new FileReader();
  reader.onload = () => {
    const imageItem = document.createElement('div');
    imageItem.className = 'image-item';
    imageItem.innerHTML = `
      <img src="${reader.result}" alt="${imageFile.name}">
      <button class="btn delete-btn">Delete</button>
    `;
    imageGallery.appendChild(imageItem);

    // Add delete functionality
    imageItem.querySelector('.delete-btn').addEventListener('click', () => {
      imageGallery.removeChild(imageItem);
    });
  };
  reader.readAsDataURL(imageFile);

  alert('Image uploaded successfully!');
  uploadImageForm.reset();
});

// Post Scheduler
const schedulePostForm = document.getElementById('schedulePostForm');
const scheduledPosts = document.getElementById('scheduledPosts');

schedulePostForm.addEventListener('submit', (e) => {
  e.preventDefault();

  const platform = document.getElementById('platform').value;
  const dateTime = document.getElementById('scheduleDateTime').value;
  const title = document.getElementById('title').value;
  const description = document.getElementById('description').value;
  const tags = document.getElementById('tags').value;

  if (!platform || !dateTime || !title || !description) {
    alert('Please complete all fields to schedule a post.');
    return;
  }

  const postItem = document.createElement('div');
  postItem.className = 'post-item';
  postItem.innerHTML = `
    <p><strong>Platform:</strong> ${platform}</p>
    <p><strong>Date & Time:</strong> ${new Date(dateTime).toLocaleString()}</p>
    <p><strong>Title:</strong> ${title}</p>
    <p><strong>Description:</strong> ${description}</p>
    <p><strong>Tags:</strong> ${tags}</p>
  `;

  scheduledPosts.appendChild(postItem);

  alert('Post scheduled successfully!');
  schedulePostForm.reset();
});
document.addEventListener('DOMContentLoaded', function () {
  const calendarEl = document.getElementById('calendar');
  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay',
    },
    events: [], // Events will be dynamically added
  });

  calendar.render();

  // Add scheduled posts to the calendar
  const schedulePostForm = document.getElementById('schedulePostForm');
  schedulePostForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const platform = document.getElementById('platform').value;
    const dateTime = document.getElementById('scheduleDateTime').value;
    const title = document.getElementById('title').value;

    if (!platform || !dateTime || !title) {
      alert('Please complete all fields to schedule a post.');
      return;
    }

    // Add event to the calendar
    calendar.addEvent({
      title: `${platform.toUpperCase()}: ${title}`,
      start: dateTime,
      allDay: false,
    });

    alert('Post scheduled and added to calendar!');
    schedulePostForm.reset();
  });
});
