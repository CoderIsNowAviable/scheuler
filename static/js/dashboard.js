document.addEventListener("DOMContentLoaded", () => {
    const menuToggle = document.querySelector(".menu-toggle");
    const navContainer = document.querySelector(".nav-container");
    const profileToggle = document.querySelector(".profile-toggle");
    const profileOptions = document.querySelector(".profile-options");

    // Toggle mobile navigation menu
    menuToggle.addEventListener("click", () => {
        navContainer.classList.toggle("open");
    });

    // Toggle profile options
    profileToggle.addEventListener("click", () => {
        profileOptions.style.display = profileOptions.style.display === "block" ? "none" : "block";
    });
});
