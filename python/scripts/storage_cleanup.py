import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import logging

class StorageManager:
    def __init__(self, storage_dir: str, max_age_days: int = 7, max_size_mb: int = 500):
        """
        Initialize Storage Manager
        
        Args:
            storage_dir (str): Base storage directory path
            max_age_days (int): Maximum age of files in days before deletion
            max_size_mb (int): Maximum total size of storage in megabytes
        """
        self.storage_dir = Path(storage_dir)
        self.pdf_dir = self.storage_dir / "pdf_uploads"
        self.txt_dir = self.storage_dir / "txt_outputs"
        self.max_age = timedelta(days=max_age_days)
        self.max_size = max_size_mb * 1024 * 1024  # Convert MB to bytes
        
        # Setup logging
        logging.basicConfig(
            filename=self.storage_dir / 'storage_cleanup.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Create directories if they don't exist
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.txt_dir.mkdir(parents=True, exist_ok=True)

    def get_file_age(self, file_path: Path) -> timedelta:
        """Get the age of a file"""
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        return datetime.now() - mtime

    def get_directory_size(self, directory: Path) -> int:
        """Calculate total size of a directory in bytes"""
        total_size = 0
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = Path(dirpath) / filename
                total_size += file_path.stat().st_size
        return total_size

    def get_all_files(self) -> list:
        """Get list of all files with their details"""
        all_files = []
        for directory in [self.pdf_dir, self.txt_dir]:
            for file_path in directory.glob('*'):
                if file_path.is_file():
                    stats = file_path.stat()
                    all_files.append({
                        'path': file_path,
                        'size': stats.st_size,
                        'mtime': stats.st_mtime,
                        'age': self.get_file_age(file_path)
                    })
        return all_files

    def cleanup_old_files(self) -> int:
        """
        Remove files older than max_age
        Returns: Number of files removed
        """
        files_removed = 0
        try:
            all_files = self.get_all_files()
            for file_info in all_files:
                file_path = file_info['path']
                age_days = file_info['age'].days
                
                if age_days > self.max_age.days:
                    file_path.unlink()
                    files_removed += 1
                    logging.info(f"Deleted old file: {file_path} (Age: {age_days} days)")
                else:
                    logging.debug(f"Keeping file: {file_path} (Age: {age_days} days)")
            
            logging.info(f"Age-based cleanup completed: removed {files_removed} files")
            return files_removed
            
        except Exception as e:
            logging.error(f"Error during age-based cleanup: {str(e)}")
            return 0

    def cleanup_by_size(self) -> int:
        """
        Remove oldest files when total size exceeds max_size
        Returns: Number of files removed
        """
        files_removed = 0
        try:
            total_size = self.get_directory_size(self.pdf_dir) + self.get_directory_size(self.txt_dir)
            logging.info(f"Current storage size: {total_size / (1024 * 1024):.2f} MB / {self.max_size / (1024 * 1024):.2f} MB")
            
            if total_size > self.max_size:
                # Get and sort files by modification time
                all_files = self.get_all_files()
                all_files.sort(key=lambda x: x['mtime'])  # Sort by modification time
                
                # Delete oldest files until under size limit
                for file_info in all_files:
                    if total_size <= self.max_size:
                        break
                        
                    file_path = file_info['path']
                    file_size = file_info['size']
                    
                    file_path.unlink()
                    total_size -= file_size
                    files_removed += 1
                    logging.info(f"Deleted file due to size limit: {file_path} (Size: {file_size / (1024 * 1024):.2f} MB)")
                
                logging.info(f"Size-based cleanup completed: removed {files_removed} files")
            else:
                logging.info("Storage size is within limits, no cleanup needed")
            
            return files_removed
            
        except Exception as e:
            logging.error(f"Error during size-based cleanup: {str(e)}")
            return 0

    def force_cleanup(self, max_age_hours: int = None) -> dict:
        """
        Force cleanup of files older than specified hours
        If max_age_hours is None, removes all files
        Returns: Cleanup statistics
        """
        files_removed = 0
        total_size_removed = 0
        
        try:
            all_files = self.get_all_files()
            for file_info in all_files:
                file_path = file_info['path']
                file_size = file_info['size']
                
                if max_age_hours is None or file_info['age'] > timedelta(hours=max_age_hours):
                    file_path.unlink()
                    files_removed += 1
                    total_size_removed += file_size
                    logging.info(f"Force deleted: {file_path}")
            
            logging.info(f"Force cleanup completed: removed {files_removed} files ({total_size_removed / (1024 * 1024):.2f} MB)")
            
            return {
                "files_removed": files_removed,
                "size_removed_mb": round(total_size_removed / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logging.error(f"Error during force cleanup: {str(e)}")
            return {"files_removed": 0, "size_removed_mb": 0}

    def cleanup(self) -> dict:
        """
        Perform complete cleanup
        Returns: Cleanup statistics
        """
        logging.info("Starting storage cleanup...")
        
        # Get initial state
        initial_size = self.get_directory_size(self.pdf_dir) + self.get_directory_size(self.txt_dir)
        initial_count = len(self.get_all_files())
        
        # Perform cleanup
        files_removed_age = self.cleanup_old_files()
        files_removed_size = self.cleanup_by_size()
        
        # Get final state
        final_size = self.get_directory_size(self.pdf_dir) + self.get_directory_size(self.txt_dir)
        final_count = len(self.get_all_files())
        
        stats = {
            "initial_files": initial_count,
            "final_files": final_count,
            "files_removed": files_removed_age + files_removed_size,
            "initial_size_mb": round(initial_size / (1024 * 1024), 2),
            "final_size_mb": round(final_size / (1024 * 1024), 2),
            "space_freed_mb": round((initial_size - final_size) / (1024 * 1024), 2)
        }
        
        logging.info(f"Storage cleanup completed: {stats}")
        return stats