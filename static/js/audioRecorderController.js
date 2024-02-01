// audioRecorderController.js
import { startRecording, stopRecording } from './audioRecorder.js';
import { uploadAudio } from './audioUploader.js';
import { updateButtonForRecording, updateButtonForNotRecording, showRecordingStoppedOnButton, restoreRecordButtonAfterUpload } from './uiController.js';

let isRecording = false;
let audioChunks = [];

const recordButton = document.getElementById("recordButton");
const statusText = document.getElementById("status");

const onDataAvailable = (event) => {
  audioChunks.push(event.data);
};

recordButton.addEventListener("click", function () {
  if (!isRecording) {
    startRecording(onDataAvailable, onStopRecording);
    statusText.innerText = "Recording...";
    updateButtonForRecording();
    startTimer(); // Start the timer
    isRecording = true;
  } else {
    stopRecording();
    stopTimer(); // Stop the timer
    statusText.innerText = "Stopping recording...";
    updateButtonForNotRecording();
  }
});

const onStopRecording = () => {
  showRecordingStoppedOnButton();  // 상태 메시지 표시
  uploadAudio(audioChunks, onUploadSuccess, onUploadFailure);
  audioChunks = [];
  isRecording = false;
};

const onUploadSuccess = (data) => {
  restoreRecordButtonAfterUpload();
  statusText.innerText = "Upload and processing complete.";
  recordButton.style.display = "block"; // Show button after upload

  // Display spectrogram image on the page
  let img = document.createElement("img");
  img.src = data.imageUrl;
  img.alt = "Spectrogram";
  statusText.appendChild(img);

  // Create and display audio player
  let audioPlayer = document.createElement("audio");
  audioPlayer.controls = true;
  audioPlayer.src = data.audioUrl;
  statusText.appendChild(audioPlayer);

  updateButtonForNotRecording();
};

const onUploadFailure = (error) => {
  console.error("There has been a problem with your fetch operation:", error);
  statusText.innerText = "Upload failed.";
  recordButton.style.display = "block"; // Show button after failed upload
  updateButtonForNotRecording();
};

recordButton.addEventListener("click", function () {
  if (!isRecording) {
    startRecording(onDataAvailable, onStopRecording);
    statusText.innerText = "Recording...";
    updateButtonForRecording();
    isRecording = true;
  } else {
    stopRecording();
    statusText.innerText = "Stopping recording...";
    updateButtonForNotRecording();
  }
});