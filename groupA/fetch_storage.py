import os
import firebase_admin
from firebase_admin import credentials, storage

def initialize_firebase():
    cred = credentials.Certificate('./pioneer_key.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'pioneer-43aee.appspot.com/reports'  # Correct bucket name without 'gs://'
    })

def download_progress(bytes_downloaded, total_bytes):
    """Callback function to log the progress of the download."""
    if total_bytes > 0:
        percent_complete = (bytes_downloaded / total_bytes) * 100
        print(f"Download progress: {percent_complete:.2f}%")

def fetch_file_from_storage(blob_name, local_file_name, download_dir="."):
    """Fetch a file from Firebase Storage and save it locally in the specified directory."""
    try:
        # Ensure the download directory exists
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        
        # Full path for the local file
        local_file_path = os.path.join(download_dir, local_file_name)
        
        # Reference to Firebase Storage bucket
        bucket = storage.bucket()
        
        # Get the blob (file) from Firebase Storage
        blob = bucket.blob(blob_name)
        
        # Get the total size of the file
        blob.reload()  # Ensure the metadata is loaded
        total_bytes = blob.size
        total_mb = total_bytes / (1024 * 1024)  # Convert bytes to MB
        print(f"File size: {total_mb:.2f} MB")
        
        # Download the file in chunks and log progress
        with open(local_file_path, 'wb') as file_obj:
            bytes_downloaded = 0
            chunk_size = 262144  # 256 KB chunks
            with blob.open("rb") as blob_file:
                while True:
                    chunk = blob_file.read(chunk_size)
                    if not chunk:
                        break
                    file_obj.write(chunk)
                    bytes_downloaded += len(chunk)
                    download_progress(bytes_downloaded, total_bytes)
        
        print(f"File {blob_name} downloaded successfully as {local_file_path}")
        
    except Exception as e:
        print(f"Error fetching file: {e}")

def list_all_files():
    """List all file names in the Firebase Storage bucket."""
    try:
        bucket = storage.bucket()
        blobs = bucket.list_blobs()
        file_names = [blob.name for blob in blobs]
        return file_names
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

if __name__ == "__main__":
    # Initialize Firebase
    initialize_firebase()
    
    # List all files in the bucket and print them
    # file_names = list_all_files()
    # print("Files in bucket:")
    # for file_name in file_names:
    #     print(file_name)
    
    # Fetch a file from storage and specify the download directory
    blob_name = 'Apple ESG 2024.pdf'  # Replace with the path of the file in your Firebase Storage
    local_file_name = 'test.pdf'  # Name to save the file locally
    download_dir = '../ESG_reports'  # Directory to save the file
    fetch_file_from_storage(blob_name, local_file_name, download_dir)