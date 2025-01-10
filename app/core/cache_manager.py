# app/core/cache_manager.py

import logging
import os
import shutil
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages application cache, including size monitoring and cleanup."""
    
    def __init__(self):
        """Initialize cache manager with settings."""
        self.settings = get_settings()
        self.last_check: Optional[datetime] = None
        self.cache_stats: Dict[str, Dict] = {}
        
        # Set default thresholds
        self.MAX_CACHE_SIZE_GB = 10.0  # Maximum cache size in GB
        self.CACHE_WARNING_THRESHOLD = 0.8  # Warning at 80% capacity
        self.CHECK_INTERVAL = timedelta(hours=1)  # Check every hour
        self.MAX_FILE_AGE = timedelta(days=30)  # Maximum file age

    def get_file_age(self, path: Path) -> timedelta:
        """Get age of a file."""
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            return datetime.now() - mtime
        except Exception as e:
            logger.error(f"Error getting file age for {path}: {e}")
            return timedelta(0)

    def scan_directory(self, path: Path) -> List[Dict[str, any]]:
        """Scan directory for files with their details."""
        files_info = []
        try:
            for entry in os.scandir(path):
                try:
                    entry_path = Path(entry.path)
                    if entry.is_file():
                        age = self.get_file_age(entry_path)
                        files_info.append({
                            'path': entry_path,
                            'size': entry.stat().st_size,
                            'age': age,
                            'is_file': True
                        })
                    elif entry.is_dir():
                        # Recursively scan subdirectories
                        files_info.extend(self.scan_directory(entry_path))
                except Exception as e:
                    logger.error(f"Error scanning {entry.path}: {e}")
        except Exception as e:
            logger.error(f"Error scanning directory {path}: {e}")
        return files_info

    def cleanup_old_files(self, max_age: Optional[timedelta] = None) -> Dict[str, int]:
        """Clean up files older than specified age."""
        max_age = max_age or self.MAX_FILE_AGE
        stats = {'removed': 0, 'failed': 0, 'size_freed': 0}
        
        # Scan both cache directories
        for cache_dir in [self.settings.CACHE_DIR, self.settings.MODEL_CACHE_DIR]:
            try:
                files_info = self.scan_directory(cache_dir)
                
                # Filter and delete old files
                for file_info in files_info:
                    if not file_info['is_file']:
                        continue
                        
                    if file_info['age'] > max_age:
                        try:
                            file_info['path'].unlink()
                            stats['removed'] += 1
                            stats['size_freed'] += file_info['size']
                            logger.debug(f"Removed old file: {file_info['path']}")
                        except Exception as e:
                            logger.error(f"Failed to remove {file_info['path']}: {e}")
                            stats['failed'] += 1
                
                # Clean up empty directories
                self.cleanup_empty_dirs(cache_dir)
                
            except Exception as e:
                logger.error(f"Error during age-based cleanup of {cache_dir}: {e}")
        
        logger.info(
            f"Age-based cleanup complete: removed {stats['removed']} files "
            f"({self.bytes_to_gb(stats['size_freed']):.2f}GB freed)"
        )
        return stats

    def cleanup_empty_dirs(self, path: Path) -> None:
        """Remove empty directories recursively."""
        try:
            for entry in os.scandir(path):
                if entry.is_dir():
                    entry_path = Path(entry.path)
                    self.cleanup_empty_dirs(entry_path)
                    
                    # Try to remove directory if empty
                    try:
                        entry_path.rmdir()
                        logger.debug(f"Removed empty directory: {entry_path}")
                    except OSError:
                        # Directory not empty, skip
                        pass
        except Exception as e:
            logger.error(f"Error cleaning up empty directories in {path}: {e}")

    def get_directory_size(self, path: Path) -> float:
        """Get directory size in bytes."""
        try:
            total_size = 0
            for entry in os.scandir(path):
                if entry.is_file():
                    total_size += entry.stat().st_size
                elif entry.is_dir():
                    total_size += self.get_directory_size(Path(entry.path))
            return total_size
        except Exception as e:
            logger.error(f"Error calculating directory size for {path}: {e}")
            return 0
    
    def bytes_to_gb(self, bytes_size: float) -> float:
        """Convert bytes to gigabytes."""
        return bytes_size / (1024 ** 3)
    
    def check_cache_size(self, force: bool = False) -> Dict[str, Dict]:
        """Check cache sizes and update stats."""
        current_time = datetime.now()
        
        # Skip if checked recently and not forced
        if not force and self.last_check and \
           (current_time - self.last_check) < self.CHECK_INTERVAL:
            return self.cache_stats
        
        try:
            # Check model cache
            model_cache_size = self.get_directory_size(self.settings.MODEL_CACHE_DIR)
            model_cache_gb = self.bytes_to_gb(model_cache_size)
            
            # Check main cache
            cache_size = self.get_directory_size(self.settings.CACHE_DIR)
            cache_gb = self.bytes_to_gb(cache_size)
            
            # Update stats
            self.cache_stats = {
                'model_cache': {
                    'size_bytes': model_cache_size,
                    'size_gb': model_cache_gb,
                    'path': str(self.settings.MODEL_CACHE_DIR)
                },
                'main_cache': {
                    'size_bytes': cache_size,
                    'size_gb': cache_gb,
                    'path': str(self.settings.CACHE_DIR)
                },
                'total': {
                    'size_bytes': model_cache_size + cache_size,
                    'size_gb': model_cache_gb + cache_gb,
                    'last_checked': current_time.isoformat()
                }
            }
            
            # Auto-cleanup if approaching limit
            total_gb = self.cache_stats['total']['size_gb']
            if total_gb >= (self.MAX_CACHE_SIZE_GB * self.CACHE_WARNING_THRESHOLD):
                logger.warning(
                    f"Cache size ({total_gb:.2f}GB) approaching maximum. "
                    "Starting automatic cleanup..."
                )
                self.cleanup_old_files()
            
            self.last_check = current_time
            return self.cache_stats
            
        except Exception as e:
            logger.error(f"Error checking cache size: {e}")
            return {}
    
    def get_cache_stats(self, force_check: bool = False) -> Dict[str, Dict]:
        """Get cache statistics."""
        return self.check_cache_size(force=force_check)
    
    def clear_cache(self, cache_type: Optional[str] = None) -> bool:
        """Clear specified cache or all caches."""
        try:
            if cache_type == "model":
                shutil.rmtree(self.settings.MODEL_CACHE_DIR)
                self.settings.MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
                logger.info("Model cache cleared")
            elif cache_type == "main":
                shutil.rmtree(self.settings.CACHE_DIR)
                self.settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)
                logger.info("Main cache cleared")
            else:
                shutil.rmtree(self.settings.CACHE_DIR)
                shutil.rmtree(self.settings.MODEL_CACHE_DIR)
                self.settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)
                self.settings.MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
                logger.info("All caches cleared")
            
            # Reset stats
            self.last_check = None
            self.cache_stats = {}
            
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

# Create singleton instance
cache_manager = CacheManager()