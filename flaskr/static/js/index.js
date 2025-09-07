// --- DOM Element References ---
const uploadArea = document.getElementById("upload-area");
const fileInput = document.getElementById("file-input");
const filesPreviewArea = document.getElementById("files-preview-area");
const fileListContainer = document.getElementById("file-list");
const addMoreBtn = document.getElementById("add-more-btn");

// --- State Management ---
let selectedFiles = [];

// --- Utility Functions ---
function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

// --- Core UI Functions ---
function renderFileList() {
  fileListContainer.innerHTML = ""; // Clear the current list

  if (selectedFiles.length === 0) {
    // If no files are left, revert to the initial upload screen
    filesPreviewArea.classList.add("hidden");
    uploadArea.classList.remove("hidden");
    return;
  }

  // Otherwise, show the preview area
  uploadArea.classList.add("hidden");
  filesPreviewArea.classList.remove("hidden");

  selectedFiles.forEach((file, index) => {
    const fileElement = document.createElement("div");
    fileElement.className =
      "flex items-center justify-between bg-gray-50 p-4 rounded-lg border";

    fileElement.innerHTML = `
        <div class="flex items-center space-x-4 overflow-hidden">
            <svg class="w-8 h-8 text-gray-500 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            <div class="overflow-hidden">
                <p class="font-semibold text-gray-800 truncate">${file.name}</p>
                <p class="text-sm text-gray-500">${formatBytes(file.size)}</p>
            </div>
        </div>
        <button data-index="${index}" class="remove-file-btn flex-shrink-0 text-red-500 hover:text-red-700 p-2 rounded-md hover:bg-red-100 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
    `;
    fileListContainer.appendChild(fileElement);
  });
}

function handleFiles(files) {
  // Add new files to our list, avoiding duplicates
  const newFiles = Array.from(files).filter(
    (file) =>
      !selectedFiles.some(
        (existingFile) =>
          existingFile.name === file.name && existingFile.size === file.size,
      ),
  );
  selectedFiles.push(...newFiles);
  renderFileList();
}

// --- Event Listeners ---

// Listen for file selection via the button
fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    handleFiles(fileInput.files);
    // Reset input so the 'change' event fires again if the same file is selected after being removed
    fileInput.value = "";
  }
});

// Listen for "Add More Files" button click
addMoreBtn.addEventListener("click", () => fileInput.click());

// Drag and Drop Listeners for the upload area
uploadArea.addEventListener("dragover", (event) => {
  event.preventDefault(); // Necessary to allow for 'drop'
  event.currentTarget.querySelector("label").classList.add("border-blue-500");
});
uploadArea.addEventListener("dragleave", (event) => {
  event.currentTarget
    .querySelector("label")
    .classList.remove("border-blue-500");
});
uploadArea.addEventListener("drop", (event) => {
  event.preventDefault();
  event.currentTarget
    .querySelector("label")
    .classList.remove("border-blue-500");
  handleFiles(event.dataTransfer.files);
});

// Event delegation for remove buttons. Listens on the container.
fileListContainer.addEventListener("click", (event) => {
  const removeButton = event.target.closest(".remove-file-btn");
  if (removeButton) {
    const indexToRemove = parseInt(removeButton.dataset.index, 10);
    selectedFiles.splice(indexToRemove, 1);
    // Re-render the list with the updated array
    renderFileList();
  }
});

const convertBtn = document.getElementById("convert-btn");

convertBtn.addEventListener("click", () => {
  if (selectedFiles.length === 0) {
    alert("Please select files to convert.");
    return;
  }

  // Use the FormData API to package the files for sending
  const formData = new FormData();
  selectedFiles.forEach((file) => {
    // The 'files[]' name must match what the Flask backend expects
    formData.append("files[]", file);
  });

  // Optional: Provide feedback to the user while uploading/converting
  convertBtn.disabled = true;
  convertBtn.textContent = "Converting... Please Wait";
  convertBtn.classList.remove("bg-green-500", "hover:bg-green-600");
  convertBtn.classList.add("bg-gray-500", "cursor-not-allowed");

  // Send the files to the backend
  fetch("/convert", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      if (response.ok) {
        // If the response is a file, it will be a blob
        return response.blob();
      }
      // If the server returned an error (e.g., 400, 500), handle it as JSON
      return response.json().then((errorData) => {
        throw new Error(errorData.error || "An unknown error occurred.");
      });
    })
    .then((blob) => {
      // Create a temporary URL for the blob and trigger a download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = "converted_documents.zip"; // The default filename for the download
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      // Reset the UI to its initial state after successful download
      selectedFiles = [];
      renderFileList();
    })
    .catch((error) => {
      // Display any errors to the user
      alert(`Conversion failed: ${error.message}`);
    })
    .finally(() => {
      // Re-enable the button regardless of success or failure
      convertBtn.disabled = false;
      convertBtn.textContent = "Convert Files";
      convertBtn.classList.add("bg-green-500", "hover:bg-green-600");
      convertBtn.classList.remove("bg-gray-500", "cursor-not-allowed");
    });
});
