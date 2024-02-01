# app/routes.py
from flask import render_template, request, jsonify
from .services import get_mel_spectrogram, draw_mel_square_spec_and_save
from .storage_utils import upload_blob, generate_signed_url
import os
from datetime import datetime
import librosa
import librosa.display
from pydub import AudioSegment
import shutil
import numpy as np

def main():
    return render_template('intro.html')

def index():
    return render_template('index.html')

def upload_file():
    temp_dir = 'temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    if 'audioFile' not in request.files:
        return 'No file part', 400

    file = request.files['audioFile']
    if file.filename == '':
        return 'No selected file', 400

    if file:
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'webm'
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = current_time + '.' + file_ext
        temp_path = os.path.join('temp', original_filename)
        file.save(temp_path)

        bucket_name = 'heartimages'
        original_destination_blob_name = f'recorded_sounds/{original_filename}'
        upload_blob(bucket_name, temp_path, original_destination_blob_name)

        wav_filename = current_time + '.wav'
        wav_path = os.path.join('temp', wav_filename)
        AudioSegment.from_file(temp_path).export(wav_path, format='wav')

                # mp3 파일로 변환
        mp3_filename = current_time + '.mp3'
        mp3_path = os.path.join('temp', mp3_filename)
        AudioSegment.from_file(wav_path).export(mp3_path, format='mp3')

        # mp3 파일을 클라우드에 업로드
        mp3_destination_blob_name = f'recorded_sounds/{mp3_filename}'
        upload_blob(bucket_name, mp3_path, mp3_destination_blob_name)

        y, sr = librosa.load(wav_path, sr=None)
        mel = get_mel_spectrogram(y, sr)
        
        img_filename = wav_filename.split('.')[0] + '.png'
        img_path = os.path.join('temp', img_filename)
        frame_stride=0.01
        draw_mel_square_spec_and_save(mel, sr, frame_stride, 'temp', img_filename)

        destination_blob_name = f'spectrograms/{img_filename}'
        upload_blob(bucket_name, img_path, destination_blob_name)

        os.remove(temp_path)
        os.remove(wav_path)
        os.remove(img_path)
        shutil.rmtree(temp_dir)

        spectrogram_signed_url = generate_signed_url(bucket_name, destination_blob_name)
        
         # 클라우드에 업로드된 mp3 파일의 URL 생성
        mp3_signed_url = generate_signed_url(bucket_name, mp3_destination_blob_name)

        return jsonify({
            'message': 'File uploaded successfully',
            'imageUrl': spectrogram_signed_url,
            'audioUrl': mp3_signed_url  # mp3 파일의 URL 반환
        })
    
def configure_routes(app):
    app.add_url_rule('/', 'main', main)
    app.add_url_rule('/index', 'index', index)
    app.add_url_rule('/upload', 'upload_file', upload_file, methods=['POST'])
