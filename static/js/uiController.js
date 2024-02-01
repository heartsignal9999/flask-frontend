// static/js/uiController.js

let timerInterval; // 타이머 인터벌을 저장할 변수
let startTime; // 녹음 시작 시간

function setRecordButtonState({ text, bgRemoveClasses, bgAddClasses, disabled }) {
  const recordButton = document.getElementById("recordButton");
  recordButton.innerText = text;
  recordButton.classList.remove(...bgRemoveClasses);
  recordButton.classList.add(...bgAddClasses);
  recordButton.disabled = disabled;
}

// 타이머를 시작하고 업데이트하는 함수
function startTimer() {
  startTime = Date.now();
  timerInterval = setInterval(updateTimer, 500); // 0.5초마다 타이머 업데이트
}

// 타이머를 화면에 표시하는 함수
function updateTimer() {
  const elapsed = Date.now() - startTime;
  const seconds = Math.floor(elapsed / 1000);
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  const formattedTime = `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
  document.getElementById("timer").innerText = formattedTime;
}

// 타이머를 정지하고 초기화하는 함수
function stopTimer() {
  clearInterval(timerInterval);
  document.getElementById("timer").innerText = "";
}

function updateButtonForRecording() {
  setRecordButtonState({
    text: "Stop Recording ",
    bgRemoveClasses: ["bg-blue-500", "hover:bg-blue-700"],
    bgAddClasses: ["bg-red-500", "hover:bg-red-700"],
    disabled: false
  });

  // 타이머 엘리먼트 추가
  const timerElement = document.createElement("span");
  timerElement.id = "timer";
  document.getElementById("recordButton").appendChild(timerElement);

  startTimer(); // 타이머 시작
}

function updateButtonForNotRecording() {
  setRecordButtonState({
    text: "Start Recording",
    bgRemoveClasses: ["bg-gray-500", "hover:bg-red-700"],
    bgAddClasses: ["bg-blue-500", "hover:bg-blue-700"],
    disabled: false
  });
}

function showRecordingStoppedOnButton() {
  setRecordButtonState({
    text: "Recording Stopped. Uploading...",
    bgRemoveClasses: ["bg-blue-500", "hover:bg-blue-700", "bg-red-500", "hover:bg-red-700"],
    bgAddClasses: ["bg-gray-500"],
    disabled: true
  });
}

function restoreRecordButtonAfterUpload() {
  updateButtonForNotRecording();
}

export const handleUploadSuccess = (data, statusText, resultContainer, recordButton) => {
  restoreRecordButtonAfterUpload();
  statusText.innerText = "Upload and processing complete.";

  // Element 생성 및 추가 함수
  const createElementAndAppend = (type, src, altText) => {
    let element = document.createElement(type);

    if (type === "img") {
      element.src = src;
      element.alt = altText || '';
    } else if (type === "audio") {
      element.controls = true;
      element.src = src;
    }

    return element;
  };

  // 기존 Element 제거 및 새 Element 추가
  const updateElement = (currentElement, type, src, altText) => {
    if (currentElement) {
      currentElement.remove();
    }
    currentElement = createElementAndAppend(type, src, altText);
    statusText.parentNode.insertBefore(currentElement, statusText);
    resultContainer.appendChild(currentElement);

    return currentElement;
  };

  // 이미지 및 오디오 플레이어 업데이트
  currentImage = updateElement(currentImage, "img", data.imageUrl, "Spectrogram");
  currentAudioPlayer = updateElement(currentAudioPlayer, "audio", data.audioUrl);

  updateButtonForNotRecording();
};

export const handleUploadFailure = (error, statusText) => {
  console.error("There has been a problem with your fetch operation:", error);
  statusText.innerText = "Upload failed.";
  updateButtonForNotRecording();
};

export { updateButtonForRecording, updateButtonForNotRecording, showRecordingStoppedOnButton, restoreRecordButtonAfterUpload };