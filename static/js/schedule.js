export function initializeSchedule() {
  const uploadBox = document.querySelector(".upload-box");
  const selectButton = document.getElementById("select-photo-btn");
  const bindAccountBtn = document.getElementById("bind-account-btn");
  const addAccountCard = document.querySelector(".add-account");
  const boundAccountCard = document.querySelector(".bound-account");

  // Drag-and-Drop Events
  uploadBox?.addEventListener("dragover", handleDragOver);
  uploadBox?.addEventListener("dragleave", handleDragLeave);
  uploadBox?.addEventListener("drop", (event) => {
    event.preventDefault();
    uploadBox.classList.remove("drag-over");
    handleFileUpload(event.dataTransfer.files, uploadBox);
  });

  // File selection via button click
  selectButton?.addEventListener("click", () => {
    console.log("Select button clicked!");
    const fileInput = createFileInput();
    fileInput.click();
  });

  // TikTok Account Binding
  bindAccountBtn?.addEventListener("click", () => {
    toggleVisibility(addAccountCard, false);
    toggleVisibility(boundAccountCard, true);
  });

  // Drag-and-Drop Handlers
  function handleDragOver(event) {
    event.preventDefault();
    uploadBox.classList.add("drag-over");
    uploadBox.setAttribute("aria-label", "Drop files to upload");
  }

  function handleDragLeave() {
    uploadBox.classList.remove("drag-over");
    uploadBox.setAttribute("aria-label", "Drag and drop files here");
  }

  // Create File Input for Button Selection
  function createFileInput() {
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = "image/*";
    fileInput.multiple = true;
    fileInput.addEventListener("change", (event) => {
      handleFileUpload(event.target.files, uploadBox);
    });
    return fileInput;
  }

  // File Upload and Preview Logic
  function handleFileUpload(files, uploadBox) {
    const validFiles = Array.from(files).filter((file) =>
      file.type.startsWith("image/")
    );

    if (validFiles.length === 0) {
      alert("Please upload valid image files.");
      return;
    }

    // Clear previous previews
    uploadBox.innerHTML = "";

    // Display uploaded images
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

  // Toggle Visibility Helper
  function toggleVisibility(element, isVisible) {
    if (element) {
      element.classList.toggle("hidden", !isVisible);
    }
  }
}
