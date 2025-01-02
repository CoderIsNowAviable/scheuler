// Select DOM elements
const uploadBox = document.querySelector(".upload-box");
const uploadText = document.querySelector(".upload-text");
const selectButton = uploadBox.querySelector("button");

// Handle file selection via button
selectButton.addEventListener("click", () => {
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = "image/*";
    fileInput.multiple = true; // Allow multiple file selection
    fileInput.addEventListener("change", (event) => {
        handleBulkFileUpload(event.target.files);
    });
    fileInput.click();
});

// Handle drag-and-drop events
uploadBox.addEventListener("dragover", (event) => {
    event.preventDefault();
    uploadBox.classList.add("drag-over");
});

uploadBox.addEventListener("dragleave", () => {
    uploadBox.classList.remove("drag-over");
});

uploadBox.addEventListener("drop", (event) => {
    event.preventDefault();
    uploadBox.classList.remove("drag-over");
    const files = Array.from(event.dataTransfer.files);
    if (files.length > 0) handleBulkFileUpload(files);
});

// Function to handle bulk file upload
function handleBulkFileUpload(files) {
    const validFiles = Array.from(files).filter(file => file.type.startsWith("image/"));

    if (validFiles.length === 0) {
        alert("Please upload valid image files.");
        return;
    }

    // Clear previous previews
    uploadBox.innerHTML = "";

    // Display each uploaded image
    validFiles.forEach((file) => {
        const reader = new FileReader();
        reader.onload = () => {
            const imgWrapper = document.createElement("div");
            imgWrapper.classList.add("img-wrapper");

            const img = document.createElement("img");
            img.src = reader.result;
            img.alt = file.name;
            img.classList.add("uploaded-img");

            const imgName = document.createElement("p");
            imgName.textContent = file.name;

            imgWrapper.appendChild(img);
            imgWrapper.appendChild(imgName);
            uploadBox.appendChild(imgWrapper);
        };
        reader.readAsDataURL(file);
    });

    uploadBox.style.border = "none";
}