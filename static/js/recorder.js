// recorder.js
let mediaRecorder;
let audioChunks = [];
let mediaStream;
let isRecording = false;

const recordButton = document.getElementById("recordButton");
const statusText = document.getElementById("status");

recordButton.addEventListener("click", function () {
  if (!isRecording) {
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        mediaStream = stream;
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();
        isRecording = true;

        statusText.innerText = "Recording...";
        updateButtonForRecording();

        mediaRecorder.addEventListener("dataavailable", (event) => {
          audioChunks.push(event.data);
        });

        mediaRecorder.addEventListener("stop", () => {
          statusText.innerText = "Recording stopped. Uploading...";
          recordButton.style.display = "none"; // Hide button during upload

          const audioBlob = new Blob(audioChunks);
          const formData = new FormData();
          formData.append("audioFile", audioBlob);

          fetch("/upload", {
            method: "POST",
            body: formData,
          })
            .then((response) => {
              if (response.ok) {
                return response.json();
              }
              throw new Error("Network response was not ok.");
            })
            .then((data) => {
              statusText.innerText = "Upload and processing complete.";
              recordButton.style.display = "block"; // Show button after upload
              updateButtonForNotRecording();

              // Display spectrogram image on the page
              let img = document.createElement("img");
              img.src = data.imageUrl;
              img.alt = "Spectrogram";
              statusText.appendChild(img);
            })
            .catch((error) => {
              console.error(
                "There has been a problem with your fetch operation:",
                error
              );
              statusText.innerText = "Upload failed.";
              recordButton.style.display = "block"; // Show button after failed upload
              updateButtonForNotRecording();
            });

          audioChunks = [];
          isRecording = false;
        });
      })
      .catch((error) => {
        console.error("Error accessing media devices:", error);
        statusText.innerText = "Error accessing media devices.";
      });
  } else {
    mediaRecorder.stop();
    mediaStream.getTracks().forEach((track) => track.stop());
    statusText.innerText = "Stopping recording...";
    isRecording = false;
  }
});

function updateButtonForRecording() {
  recordButton.innerText = "Stop Recording";
  recordButton.classList.remove("bg-blue-500", "hover:bg-blue-700");
  recordButton.classList.add("bg-red-500", "hover:bg-red-700");
}

function updateButtonForNotRecording() {
  recordButton.innerText = "Start Recording";
  recordButton.classList.remove("bg-red-500", "hover:bg-red-700");
  recordButton.classList.add("bg-blue-500", "hover:bg-blue-700");
}
