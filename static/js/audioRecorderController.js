// audioRecorderController.js
import { startRecording, stopRecording } from './audioRecorder.js';
import { uploadAudio } from './audioUploader.js';
import { updateButtonForRecording, updateButtonForNotRecording, showRecordingStoppedOnButton, restoreRecordButtonAfterUpload } from './uiController.js';

let isRecording = false;
let audioChunks = [];
let currentAudioPlayer = null;
let currentImage = null;

const recordButton = document.getElementById("recordButton");
const statusText = document.getElementById("status");

const onDataAvailable = (event) => {
  audioChunks.push(event.data);
};

const onStopRecording = () => {
  showRecordingStoppedOnButton();  // 상태 메시지 표시
  uploadAudio(audioChunks, onUploadSuccess, onUploadFailure);
  audioChunks = [];
  isRecording = false;
};

const resultContainer = document.getElementById("resultContainer");

const onUploadSuccess = (data) => {
  restoreRecordButtonAfterUpload();
  statusText.innerText = "녹음 업로드와 처리가 완료되었습니다."; 

  // 기존 이미지 제거
  if (currentImage) {
    currentImage.remove();
  }

  // 새 이미지 생성 및 저장
  let img = document.createElement("img");
  img.src = data.imageUrl;
  img.alt = "Spectrogram";
  currentImage = img; // 현재 이미지를 저장

  // 기존 오디오 플레이어 제거
  if (currentAudioPlayer) {
    currentAudioPlayer.remove();
  }

  // 새 오디오 플레이어 생성 및 저장
  let audioPlayer = document.createElement("audio");
  audioPlayer.controls = true;
  audioPlayer.src = data.audioUrl;
  currentAudioPlayer = audioPlayer; // 현재 오디오 플레이어를 저장

  // statusText 요소 바로 전에 이미지와 오디오 플레이어 추가
  statusText.parentNode.insertBefore(img, statusText);
  statusText.parentNode.insertBefore(audioPlayer, statusText);

  resultContainer.appendChild(img);
  resultContainer.appendChild(audioPlayer);

  updateButtonForNotRecording();
};

const onUploadFailure = (error) => {
  console.error("There has been a problem with your fetch operation:", error);
  statusText.innerText = "Upload failed.";
  recordButton.style.display = "block"; // Show button after failed upload
  updateButtonForNotRecording();
};

recordButton.addEventListener("click", function () {
  // 버튼이 비활성화된 상태에서는 아무런 동작도 수행하지 않습니다.
  if (recordButton.disabled) {
    return;
  }

  if (!isRecording) {
    startRecording(onDataAvailable, onStopRecording);
    statusText.innerText = "녹음 중입니다. 5초 이상 심장음을 녹음하세요.";
    updateButtonForRecording();
    isRecording = true;
  } else {
    stopRecording();
    statusText.innerText = "녹음파일 처리중...";
    updateButtonForNotRecording();
  }
});