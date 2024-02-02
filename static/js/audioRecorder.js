// audioRecorder.js
let mediaRecorder;
let audioChunks = [];
let mediaStream;

export const startRecording = (onDataAvailable, onStop, onAccessGranted, onAccessDenied) => {
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then((stream) => {
      // Access granted callback
      if (typeof onAccessGranted === 'function') {
        onAccessGranted();
      }
      mediaStream = stream;
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.start();

      mediaRecorder.addEventListener("dataavailable", onDataAvailable);
      mediaRecorder.addEventListener("stop", onStop);
    })
    .catch((error) => {
      console.error("Error accessing media devices:", error);
      // Access denied callback
      if (typeof onAccessDenied === 'function') {
        onAccessDenied();
      }
    });
};

export const stopRecording = () => {
  mediaRecorder.stop();
  mediaStream.getTracks().forEach((track) => track.stop());
};
