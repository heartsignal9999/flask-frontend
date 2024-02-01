# main.py
from flask import Flask, render_template, request, jsonify
from google.cloud import storage
from google.cloud.storage.blob import Blob
import os
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
from datetime import datetime, timedelta
import shutil 

app = Flask(__name__, static_folder='static')

@app.route('/')
def main():
    return render_template('intro.html')

@app.route('/index')
def index():
    return render_template('index.html')

# Mel 범위로 변환
def get_mel_spectrogram(wave_form, sample_rate, n_mels=96, frame_length=0.025, frame_stride=0.01):
    """
    Convert an audio waveform to a Mel spectrogram.

    :param wave_form: NumPy array of audio waveform.
    :param sample_rate: Sampling rate of the audio.
    :param n_mels: Number of Mel bands to generate.
    :param frame_length: Length of each frame in seconds.
    :param frame_stride: Stride between successive frames in seconds.
    :return: Mel spectrogram (2D NumPy array).
    """
    # Calculate the number of samples per frame and stride
    win_length = int(round(sample_rate * frame_length))
    hop_length = int(round(sample_rate * frame_stride))

    # Calculate the number of FFT components (n_fft) as the next power of two from win_length
    n_fft = 2 ** int(np.ceil(np.log2(win_length)))

    # Compute the Mel spectrogram
    mel_spectrogram = librosa.feature.melspectrogram(y=wave_form, sr=sample_rate, n_fft=n_fft,
                                                     hop_length=hop_length, win_length=win_length,
                                                     n_mels=n_mels)
    return mel_spectrogram

# 스펙트로그램 그리고 저장하기
def draw_mel_square_spec_and_save(mel, sample_rate, frame_stride, save_path, filename):
    """
    Draw a square Mel spectrogram and save it to a file.

    :param mel: Mel spectrogram (2D NumPy array).
    :param sample_rate: Sampling rate of the original audio.
    :param frame_stride: Stride between successive frames in seconds.
    :param save_path: Path to save the spectrogram image.
    :param filename: Filename for saving the image.
    """
    # Convert Mel spectrogram to Decibel scale
    S_dB = librosa.power_to_db(mel, ref=np.max)

    # Calculate hop length for time alignment
    hop_length = int(round(sample_rate * frame_stride))

    # Calculate the total duration of the audio in seconds
    total_duration_sec = mel.shape[1] * frame_stride

    # Calculate the width of the figure (1 inch per second)
    fig_width = total_duration_sec  # 1 second = 1 inch

    # Create a figure with a fixed height of 3 inches and a variable width
    fig, ax = plt.subplots(figsize=(fig_width, 3), dpi=95)  # 3 inches tall, variable width

    # Display the Mel spectrogram
    librosa.display.specshow(S_dB, sr=sample_rate, hop_length=hop_length)
    ax.set_aspect('auto')

    # Save and display the spectrogram image
    print(f"{filename} spectrogram saved")
    plt.tight_layout()
    full_save_path = os.path.join(save_path, filename)
    plt.savefig(full_save_path, bbox_inches='tight', pad_inches=0)
    plt.colorbar(format='%+2.0f dB')
    plt.show()

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")


def generate_signed_url(bucket_name, blob_name):
    """Generate a signed URL for the blob. This URL is temporary."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        expiration=timedelta(hours=1),  # URL will be valid for 1 hour
        version="v4"
    )
    return url

@app.route('/upload', methods=['POST'])
def upload_file():
    # temp 폴더가 없으면 생성
    temp_dir = 'temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    if 'audioFile' not in request.files:
        return 'No file part', 400

    file = request.files['audioFile']
    if file.filename == '':
        return 'No selected file', 400

    if file:
        # 파일 확장자 추출
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'webm'

        # 현재 시간을 기반으로 한 파일명 생성
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = current_time + '.' + file_ext
        temp_path = os.path.join('temp', original_filename)

        # 원본 녹음 파일 저장
        file.save(temp_path)

        # 원본 파일을 Google Cloud Storage에 업로드
        bucket_name = 'heartimages'
        original_destination_blob_name = f'recorded_sounds/{original_filename}'
        upload_blob(bucket_name, temp_path, original_destination_blob_name)

        # 녹음 파일을 WAV로 변환하고 temp 폴더에 저장
        wav_filename = current_time + '.wav'
        wav_path = os.path.join('temp', wav_filename)
        AudioSegment.from_file(temp_path).export(wav_path, format='wav')

        # WAV 파일 처리 및 Mel 스펙트로그램 생성
        y, sr = librosa.load(wav_path, sr=None)
        mel = get_mel_spectrogram(y, sr)
        
        # 스펙트로그램 이미지를 temp 폴더에 저장
        img_filename = wav_filename.split('.')[0] + '.png'
        img_path = os.path.join('temp', img_filename)
        frame_stride=0.01
        draw_mel_square_spec_and_save(mel, sr, frame_stride, 'temp', img_filename)

        # 스펙트로그램 이미지를 Google Cloud Storage에 업로드
        destination_blob_name = f'spectrograms/{img_filename}'
        upload_blob(bucket_name, img_path, destination_blob_name)


        # 로컬 temp 폴더의 파일 삭제
        os.remove(temp_path)
        os.remove(wav_path)
        os.remove(img_path)

        # temp 디렉토리 자체를 삭제합니다.
        shutil.rmtree(temp_dir)

        # Generate signed URL for the spectrogram image
        signed_url = generate_signed_url(bucket_name, destination_blob_name)

        # Return the signed URL in the response
        return jsonify({'message': 'File uploaded successfully', 'imageUrl': signed_url})

# 실행코드
if __name__ == '__main__':
    if not os.path.exists('temp'):
        os.makedirs('temp')
    app.run(debug=True)