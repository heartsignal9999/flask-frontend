// static/js/uiController.js
function updateButtonForRecording() {
    const recordButton = document.getElementById("recordButton");
    recordButton.innerText = "Stop Recording";
    recordButton.classList.remove("bg-blue-500", "hover:bg-blue-700");
    recordButton.classList.add("bg-red-500", "hover:bg-red-700");
  }
  
  function updateButtonForNotRecording() {
    const recordButton = document.getElementById("recordButton");
    recordButton.innerText = "Start Recording";
    recordButton.classList.remove("bg-red-500", "hover:bg-red-700");
    recordButton.classList.add("bg-blue-500", "hover:bg-blue-700");
  }
  
  function showRecordingStoppedOnButton() {
    const recordButton = document.getElementById("recordButton");
    recordButton.innerText = "Recording Stopped. Uploading...";
    recordButton.classList.remove("bg-blue-500", "hover:bg-blue-700");
    recordButton.classList.add("bg-gray-500");
    recordButton.disabled = true;  // 버튼을 비활성화합니다.
  }
  
  function restoreRecordButtonAfterUpload() {
    const recordButton = document.getElementById("recordButton");
    recordButton.innerText = "Start Recording";
    recordButton.classList.remove("bg-gray-500");
    recordButton.classList.add("bg-blue-500", "hover:bg-blue-700");
    recordButton.disabled = false;  // 버튼을 다시 활성화합니다.
  }
  
  export { updateButtonForRecording, updateButtonForNotRecording, showRecordingStoppedOnButton, restoreRecordButtonAfterUpload };
  