# app.py
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from google.cloud import storage
import os
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from pydub import AudioSegment


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

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audioFile' not in request.files:
        return 'No file part', 400

    file = request.files['audioFile']
    if file.filename == '':
        return 'No selected file', 400

    if file:
        # 파일 저장 및 처리 로직
        filename = secure_filename(file.filename)
        temp_path = os.path.join('temp', filename)
        file.save(temp_path)

        # WebM을 WAV로 변환
        wav_filename = filename.split('.')[0] + '.wav'
        AudioSegment.from_file(temp_path).export(wav_filename, format='wav')

        # WAV 파일 처리 및 Mel 스펙트로그램 생성
        y, sr = librosa.load(wav_filename, sr=None)
        mel = get_mel_spectrogram(y, sr)
        
        # 스펙트로그램 이미지 저장
        img_filename = wav_filename.split('.')[0] + '.png'
        frame_stride=0.01
        draw_mel_square_spec_and_save(mel, sr, frame_stride, 'static', img_filename)

        # 임시 파일 삭제
        os.remove(temp_path)
        os.remove(wav_filename)

        # 이미지 URL 반환
        return f'File uploaded and processed successfully. Image URL: /static/{img_filename}', 200

def call_cloud_function(file_path):
    url = "https://REGION-PROJECT_ID.cloudfunctions.net/FUNCTION_NAME"  # 실제 URL로 대체해야 함

    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)

    return response.text

# 실행코드
if __name__ == '__main__':
    if not os.path.exists('temp'):
        os.makedirs('temp')
    app.run(debug=True)