import os
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Iterator, Optional, Set


class FileFormatDetector(ABC):
    """Base class for detecting file formats."""
    
    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """Determine if this detector can handle the given file."""
        pass
    
    @abstractmethod
    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata specific to this file format."""
        pass


class CsvFormatDetector(FileFormatDetector):
    """Detector for CSV files."""
    
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == '.csv'
    
    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        # Could add CSV-specific metadata extraction here
        # For example, check header, delimiter, etc.
        return {
            'format': 'csv',
            'size_bytes': file_path.stat().st_size,
            'last_modified': file_path.stat().st_mtime
        }


class JsonFormatDetector(FileFormatDetector):
    """Detector for JSON files."""
    
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == '.json'
    
    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        # Could add JSON-specific metadata extraction here
        return {
            'format': 'json',
            'size_bytes': file_path.stat().st_size,
            'last_modified': file_path.stat().st_mtime
        }


class FileScanner:
    """Scans directories for data files and extracts metadata."""
    
    def __init__(self):
        self.format_detectors: List[FileFormatDetector] = []
        
    def register_detector(self, detector: FileFormatDetector) -> None:
        """Register a new format detector."""
        self.format_detectors.append(detector)
        
    def scan_directory(self, directory_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """Scan a directory for files that match registered formats."""
        results = []
        scan_path = Path(directory_path)
        
        if not scan_path.exists() or not scan_path.is_dir():
            raise ValueError(f"Invalid directory path: {directory_path}")
        
        # Determine how to walk the directory tree based on recursive flag
        if recursive:
            file_paths = scan_path.rglob('*')
        else:
            file_paths = scan_path.glob('*')
            
        # Filter only files (exclude directories)
        file_paths = [p for p in file_paths if p.is_file()]
        
        for file_path in file_paths:
            for detector in self.format_detectors:
                if detector.can_handle(file_path):
                    metadata = detector.get_metadata(file_path)
                    metadata.update({
                        'path': str(file_path),
                        'name': file_path.name,
                    })
                    results.append(metadata)
                    break  # Once a detector handles it, move to next file
                    
        return results


# Example usage
if __name__ == "__main__":
    scanner = FileScanner()
    scanner.register_detector(CsvFormatDetector())
    scanner.register_detector(JsonFormatDetector())
    
    # Add this to demonstrate extensibility - just uncomment when needed
    # class ParquetFormatDetector(FileFormatDetector):
    #     def can_handle(self, file_path: Path) -> bool:
    #         return file_path.suffix.lower() == '.parquet'
    #
    #     def get_metadata(self, file_path: Path) -> Dict[str, Any]:
    #         return {
    #             'format': 'parquet',
    #             'size_bytes': file_path.stat().st_size,
    #             'last_modified': file_path.stat().st_mtime
    #         }
    # scanner.register_detector(ParquetFormatDetector())
    
    results = scanner.scan_directory("./data_directory")
    
    # Display results
    for file_info in results:
        print(f"Found {file_info['format']} file: {file_info['path']}")
        print(f"  Size: {file_info['size_bytes']} bytes")