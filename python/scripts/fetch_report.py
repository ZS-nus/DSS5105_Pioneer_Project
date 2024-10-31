import firebase_admin
from firebase_admin import credentials, storage
from pathlib import Path
from typing import Dict
from config import FIREBASE_CONFIG
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('firebase_storage')

class FirebaseStorageManager:
    def __init__(self, credential_path: str, storage_dir: Path):
        self.initialized = False
        self.storage_dir = Path(storage_dir)
        self.credential_path = Path(credential_path)
        self.storage_bucket = FIREBASE_CONFIG["storage_bucket"]
        logger.info(f"Initializing FirebaseStorageManager with bucket: {self.storage_bucket}")
        self.initialize_firebase()

    def initialize_firebase(self):
        if not self.initialized:
            try:
                if not firebase_admin._apps:
                    logger.info("Initializing Firebase Admin SDK")
                    cred = credentials.Certificate(FIREBASE_CONFIG)
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': self.storage_bucket
                    })
                    logger.info("Firebase Admin SDK initialized successfully")
                self.initialized = True
            except Exception as e:
                logger.error(f"Firebase initialization failed: {str(e)}")
                raise Exception(f"Firebase initialization failed: {str(e)}")

    def download_progress(self, bytes_downloaded: int, total_bytes: int) -> None:
        """Log download progress"""
        if total_bytes > 0:
            percent_complete = (bytes_downloaded / total_bytes) * 100
            print(f"Download progress: {percent_complete:.2f}%")

    def fetch_file(self, blob_name: str) -> Dict:
        """Fetch a file from Firebase Storage and save it locally"""
        logger.info(f"Attempting to fetch file: {blob_name}")
        try:
            # Ensure the download directory exists
            pdf_dir = self.storage_dir / "pdf_uploads"
            pdf_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Storage directory confirmed: {pdf_dir}")
            
            # Add 'reports/' prefix if not present
            if not blob_name.startswith('reports/'):
                blob_name = f"reports/{blob_name}"
            logger.info(f"Using blob name with prefix: {blob_name}")
            
            # Full path for the local file
            local_file_name = Path(blob_name).name  # Extract just the filename
            local_file_path = pdf_dir / local_file_name
            
            # Reference to Firebase Storage bucket
            bucket = storage.bucket()
            blob = bucket.blob(blob_name)
            
            # Check if file exists in Firebase
            if not blob.exists():
                logger.warning(f"File not found in Firebase Storage: {blob_name}")
                return {
                    "status": "error",
                    "message": f"File '{blob_name}' not found in storage"
                }
            
            logger.info(f"File found in Firebase Storage: {blob_name}")
            
            # Get file size
            blob.reload()
            total_bytes = blob.size
            total_mb = total_bytes / (1024 * 1024)
            logger.info(f"File size: {total_mb:.2f} MB")
            
            # Download the file in chunks
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
                        self.download_progress(bytes_downloaded, total_bytes)
            
            logger.info(f"File downloaded successfully to: {local_file_path}")
            return {
                "status": "success",
                "message": "File downloaded successfully",
                "details": {
                    "file_name": local_file_name,
                    "file_path": str(local_file_path),
                    "size_mb": round(total_mb, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error downloading file {blob_name}: {str(e)}")
            return {
                "status": "error",
                "message": f"Error downloading file: {str(e)}"
            }

    def list_files(self) -> Dict:
        """List all files in the Firebase Storage bucket"""
        logger.info("Attempting to list files in Firebase Storage")
        try:
            bucket = storage.bucket()
            blobs = bucket.list_blobs()
            files = [{
                "name": blob.name,
                "size_mb": round(blob.size / (1024 * 1024), 2),
                "updated": blob.updated.isoformat()
            } for blob in blobs]
            
            logger.info(f"Successfully listed {len(files)} files")
            return {
                "status": "success",
                "files": files
            }
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return {
                "status": "error",
                "message": f"Error listing files: {str(e)}"
            }