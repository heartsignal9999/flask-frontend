// audioUploader.js
export const uploadAudio = (audioChunks, onUploadSuccess, onUploadFailure) => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
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
    .then(onUploadSuccess)
    .catch(onUploadFailure);
  };
  