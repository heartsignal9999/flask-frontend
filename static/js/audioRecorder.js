// audioRecorder.js
let mediaRecorder;
let audioChunks = [];
let mediaStream;

export const startRecording = (onDataAvailable, onStop, onAccessGranted) => {
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then((stream) => {
      // Call the onAccessGranted callback
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
    });
};

export const stopRecording = () => {
  mediaRecorder.stop();
  mediaStream.getTracks().forEach((track) => track.stop());
};
