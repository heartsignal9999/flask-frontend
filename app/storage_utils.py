# storage_utils.py
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