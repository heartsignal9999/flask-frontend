import os
from datetime import datetime
import shutil
from flask import request, jsonify
from .audio_utils import convert_to_mp3, process_audio_and_upload
from google.cloud import storage
from datetime import timedelta

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

async def save_original_file(file, temp_dir):
    """
    Saves the original file in the temporary directory.
    """
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'webm'
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    original_filename = current_time + '.' + file_ext
    temp_path = os.path.join(temp_dir, original_filename)
    file.save(temp_path)
    return temp_path, file_ext, original_filename

async def convert_and_upload(temp_path, file_ext, temp_dir, bucket_name, current_time):
    """
    Converts the file to MP3 and uploads it.
    """
    # Convert to MP3 if necessary
    mp3_filename = current_time + '.mp3'
    mp3_path = os.path.join(temp_dir, mp3_filename)
    if file_ext != 'mp3':
        convert_to_mp3(temp_path, mp3_path)  # Convert to MP3
    else:
        mp3_path = temp_path

    mp3_destination_blob_name = f'recorded_sounds/{mp3_filename}'
    upload_blob(bucket_name, mp3_path, mp3_destination_blob_name)
    return mp3_path, mp3_destination_blob_name

async def upload_file():
    """
    Handles the file upload process.
    """
    temp_dir = 'temp'
    os.makedirs(temp_dir, exist_ok=True)  # Create temp directory

    if 'audioFile' not in request.files:
        return 'No file part', 400

    file = request.files['audioFile']
    if file.filename == '':
        return 'No selected file', 400

    if file:
        bucket_name = 'heartimages'
        temp_path, file_ext, original_filename = await save_original_file(file, temp_dir)
        original_destination_blob_name = f'recorded_sounds/{original_filename}'
        upload_blob(bucket_name, temp_path, original_destination_blob_name)

        mp3_path, mp3_destination_blob_name = await convert_and_upload(temp_path, file_ext, temp_dir, bucket_name, original_filename.split('.')[0])
        img_path = process_audio_and_upload(mp3_path, temp_dir, original_filename.split('.')[0])

        destination_blob_name = f'spectrograms/{original_filename.split(".")[0]}.png'
        upload_blob(bucket_name, img_path, destination_blob_name)

        spectrogram_signed_url = generate_signed_url(bucket_name, destination_blob_name)
        mp3_signed_url = generate_signed_url(bucket_name, mp3_destination_blob_name)

        shutil.rmtree(temp_dir)  # Clean up the temp directory

        return jsonify({
            'message': 'File uploaded successfully',
            'imageUrl': spectrogram_signed_url,
            'audioUrl': mp3_signed_url
        })
