# app/uploader.py
import os
from datetime import datetime, timedelta
import shutil
from flask import request, jsonify
from google.cloud import storage
from .audio_utils import convert_to_wav, process_audio_and_save
from config import BUCKET_NAME

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
    url = blob.generate_signed_url(expiration=timedelta(hours=1), version="v4")
    return url

def save_original_file(file, temp_dir):
    """Saves the original file in the temporary directory."""
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'webm'
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    original_filename = f"{current_time}.{file_ext}"
    temp_path = os.path.join(temp_dir, original_filename)
    file.save(temp_path)
    return temp_path, file_ext, original_filename

def convert_and_upload(temp_path, file_ext, temp_dir, bucket_name, current_time):
    """Converts the file to WAV and uploads it."""
    wav_filename = f"{current_time}.wav"
    wav_path = os.path.join(temp_dir, wav_filename)
    
    if file_ext != 'wav':
        convert_to_wav(temp_path, wav_path)
    
    wav_destination_blob_name = f'recorded_sounds/{wav_filename}'
    upload_blob(bucket_name, wav_path, wav_destination_blob_name)
    return wav_path, wav_destination_blob_name

async def upload_file():
    """Handles the file upload process."""
    cache_dir = 'cache'
    temp_dir = 'temp'

    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    if 'audioFile' not in request.files:
        return 'No file part', 400

    file = request.files['audioFile']
    if file.filename == '':
        return 'No selected file', 400

    if file:
        bucket_name = BUCKET_NAME
        temp_path, file_ext, original_filename = save_original_file(file, cache_dir)
        wav_path, wav_destination_blob_name = convert_and_upload(temp_path, file_ext, cache_dir, bucket_name, original_filename.split('.')[0])
        img_path = process_audio_and_save(wav_path, cache_dir, original_filename.split('.')[0])

        destination_blob_name = f'spectrograms/{original_filename.split(".")[0]}.png'
        upload_blob(bucket_name, img_path, destination_blob_name)

        spectrogram_signed_url = generate_signed_url(bucket_name, destination_blob_name)
        wav_signed_url = generate_signed_url(bucket_name, wav_destination_blob_name)

        # shutil.rmtree(temp_dir)  # Clean up the temp directory

        return jsonify({
            'message': 'File uploaded successfully',
            'imageUrl': spectrogram_signed_url,
            'audioUrl': wav_signed_url
        })
