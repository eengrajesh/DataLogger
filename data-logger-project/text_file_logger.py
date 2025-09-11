"""
Text File Logger Module for DataLogger System
Handles raw data logging to text files with automatic rotation
"""

import os
import csv
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import threading
from typing import Dict, List, Optional, Tuple
import json

class TextFileLogger:
    """
    Handles logging temperature data to text files with rotation and compression
    """
    
    def __init__(self, base_path: str = None):
        """
        Initialize the text file logger
        
        Args:
            base_path: Base directory for data files (default: ./data)
        """
        if base_path is None:
            base_path = os.path.join(os.path.dirname(__file__), 'data')
        
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / 'raw'
        self.daily_path = self.base_path / 'daily'
        self.exports_path = self.base_path / 'exports'
        self.compressed_path = self.base_path / 'compressed'
        
        # Create directories
        self._create_directories()
        
        # Thread lock for file operations
        self._lock = threading.Lock()
        
        # Configuration
        self.max_raw_files = 48  # Keep 48 hours of raw files
        self.max_daily_files = 30  # Keep 30 days of daily files
        self.compress_after_days = 7  # Compress files older than 7 days
        
        # Current file handles
        self._current_raw_file = None
        self._current_raw_filename = None
        self._current_hour = None
        
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        for path in [self.raw_path, self.daily_path, self.exports_path, self.compressed_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def _get_raw_filename(self, timestamp: datetime = None) -> str:
        """Get the raw data filename for the given timestamp"""
        if timestamp is None:
            timestamp = datetime.now()
        return f"{timestamp.strftime('%Y-%m-%d_%H')}.txt"
    
    def _get_daily_filename(self, timestamp: datetime = None) -> str:
        """Get the daily data filename for the given timestamp"""
        if timestamp is None:
            timestamp = datetime.now()
        return f"{timestamp.strftime('%Y-%m-%d')}.txt"
    
    def _ensure_raw_file_open(self, timestamp: datetime):
        """Ensure the correct raw file is open for writing"""
        current_hour = timestamp.hour
        filename = self._get_raw_filename(timestamp)
        
        if self._current_raw_filename != filename or self._current_hour != current_hour:
            # Close current file if open
            if self._current_raw_file:
                self._current_raw_file.close()
            
            # Open new file
            filepath = self.raw_path / filename
            self._current_raw_file = open(filepath, 'a', encoding='utf-8')
            self._current_raw_filename = filename
            self._current_hour = current_hour
            
            # Write header if file is new
            if filepath.stat().st_size == 0:
                self._current_raw_file.write("timestamp,channel,temperature,calibrated_temp,unit\n")
                self._current_raw_file.flush()
    
    def log_reading(self, channel: int, temperature: float, calibrated_temp: float = None, timestamp: datetime = None):
        """
        Log a temperature reading to text file
        
        Args:
            channel: Thermocouple channel (1-8)
            temperature: Raw temperature reading
            calibrated_temp: Calibrated temperature (optional)
            timestamp: Reading timestamp (optional, defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        if calibrated_temp is None:
            calibrated_temp = temperature
        
        with self._lock:
            try:
                self._ensure_raw_file_open(timestamp)
                
                # Format: timestamp,channel,temperature,calibrated_temp,unit
                line = f"{timestamp.isoformat()},{channel},{temperature:.3f},{calibrated_temp:.3f},C\n"
                self._current_raw_file.write(line)
                self._current_raw_file.flush()
                
                print(f"[TextLogger] Logged CH{channel}: {calibrated_temp:.2f}°C to {self._current_raw_filename}")
                
            except Exception as e:
                print(f"[TextLogger] Error logging reading: {e}")
    
    def consolidate_daily_file(self, date: datetime = None):
        """
        Consolidate hourly raw files into a daily file
        
        Args:
            date: Date to consolidate (defaults to yesterday)
        """
        if date is None:
            date = datetime.now().date() - timedelta(days=1)
        else:
            date = date.date() if isinstance(date, datetime) else date
        
        daily_filename = f"{date.strftime('%Y-%m-%d')}.txt"
        daily_filepath = self.daily_path / daily_filename
        
        # Find all raw files for this date
        raw_files = []
        for hour in range(24):
            raw_filename = f"{date.strftime('%Y-%m-%d')}_{hour:02d}.txt"
            raw_filepath = self.raw_path / raw_filename
            if raw_filepath.exists():
                raw_files.append(raw_filepath)
        
        if not raw_files:
            print(f"[TextLogger] No raw files found for {date}")
            return
        
        # Consolidate files
        try:
            with open(daily_filepath, 'w', encoding='utf-8', newline='') as daily_file:
                writer = csv.writer(daily_file)
                writer.writerow(['timestamp', 'channel', 'temperature', 'calibrated_temp', 'unit'])
                
                records_written = 0
                for raw_file in sorted(raw_files):
                    with open(raw_file, 'r', encoding='utf-8') as rf:
                        reader = csv.reader(rf)
                        next(reader, None)  # Skip header
                        for row in reader:
                            if len(row) >= 4:  # Valid row
                                writer.writerow(row)
                                records_written += 1
            
            print(f"[TextLogger] Consolidated {len(raw_files)} files into {daily_filename} ({records_written} records)")
            
        except Exception as e:
            print(f"[TextLogger] Error consolidating daily file: {e}")
    
    def cleanup_old_files(self):
        """Remove old files based on retention policy"""
        now = datetime.now()
        
        # Clean up old raw files
        try:
            raw_files = list(self.raw_path.glob('*.txt'))
            for file_path in raw_files:
                # Parse timestamp from filename
                try:
                    date_hour = file_path.stem  # e.g., "2024-01-15_10"
                    file_time = datetime.strptime(date_hour, '%Y-%m-%d_%H')
                    if (now - file_time).total_seconds() > (self.max_raw_files * 3600):
                        file_path.unlink()
                        print(f"[TextLogger] Removed old raw file: {file_path.name}")
                except ValueError:
                    continue  # Skip files with invalid names
        except Exception as e:
            print(f"[TextLogger] Error cleaning up raw files: {e}")
        
        # Clean up old daily files
        try:
            daily_files = list(self.daily_path.glob('*.txt'))
            for file_path in daily_files:
                try:
                    date_str = file_path.stem  # e.g., "2024-01-15"
                    file_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    if (now.date() - file_date).days > self.max_daily_files:
                        file_path.unlink()
                        print(f"[TextLogger] Removed old daily file: {file_path.name}")
                except ValueError:
                    continue
        except Exception as e:
            print(f"[TextLogger] Error cleaning up daily files: {e}")
    
    def compress_old_files(self):
        """Compress files older than compression threshold"""
        now = datetime.now()
        threshold = now - timedelta(days=self.compress_after_days)
        
        # Compress old daily files
        try:
            daily_files = list(self.daily_path.glob('*.txt'))
            for file_path in daily_files:
                try:
                    date_str = file_path.stem
                    file_date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    if file_date < threshold:
                        compressed_path = self.compressed_path / f"{file_path.name}.gz"
                        with open(file_path, 'rb') as f_in:
                            with gzip.open(compressed_path, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        
                        file_path.unlink()
                        print(f"[TextLogger] Compressed and removed: {file_path.name}")
                        
                except ValueError:
                    continue
        except Exception as e:
            print(f"[TextLogger] Error compressing files: {e}")
    
    def get_readings_by_date_range(self, start_date: datetime, end_date: datetime, 
                                  channels: List[int] = None) -> List[Dict]:
        """
        Get readings from text files for a date range
        
        Args:
            start_date: Start date/time
            end_date: End date/time
            channels: List of channels to include (None = all)
        
        Returns:
            List of reading dictionaries
        """
        readings = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            # Try daily file first
            daily_file = self.daily_path / f"{current_date.strftime('%Y-%m-%d')}.txt"
            
            if daily_file.exists():
                readings.extend(self._read_file(daily_file, start_date, end_date, channels))
            else:
                # Fall back to raw files for current/recent dates
                for hour in range(24):
                    raw_file = self.raw_path / f"{current_date.strftime('%Y-%m-%d')}_{hour:02d}.txt"
                    if raw_file.exists():
                        readings.extend(self._read_file(raw_file, start_date, end_date, channels))
            
            current_date += timedelta(days=1)
        
        return sorted(readings, key=lambda x: x['timestamp'])
    
    def _read_file(self, file_path: Path, start_date: datetime, end_date: datetime, 
                  channels: List[int] = None) -> List[Dict]:
        """Read and filter data from a single file"""
        readings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        timestamp = datetime.fromisoformat(row['timestamp'])
                        channel = int(row['channel'])
                        
                        # Filter by date range
                        if not (start_date <= timestamp <= end_date):
                            continue
                        
                        # Filter by channels
                        if channels and channel not in channels:
                            continue
                        
                        readings.append({
                            'timestamp': timestamp,
                            'channel': channel,
                            'temperature': float(row['temperature']),
                            'calibrated_temp': float(row['calibrated_temp']),
                            'unit': row.get('unit', 'C')
                        })
                    except (ValueError, KeyError) as e:
                        continue  # Skip invalid rows
                        
        except Exception as e:
            print(f"[TextLogger] Error reading file {file_path}: {e}")
        
        return readings
    
    def generate_csv_export(self, start_date: datetime, end_date: datetime, 
                           channels: List[int] = None, include_raw: bool = False) -> str:
        """
        Generate CSV export file from text data
        
        Args:
            start_date: Start date/time
            end_date: End date/time
            channels: List of channels to include
            include_raw: Include raw temperature values
        
        Returns:
            Path to generated CSV file
        """
        # Generate filename
        export_filename = f"export_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        export_path = self.exports_path / export_filename
        
        # Get readings
        readings = self.get_readings_by_date_range(start_date, end_date, channels)
        
        # Write CSV
        try:
            with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'channel', 'calibrated_temp']
                if include_raw:
                    fieldnames.insert(2, 'raw_temp')
                fieldnames.append('unit')
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for reading in readings:
                    row = {
                        'timestamp': reading['timestamp'].isoformat(),
                        'channel': reading['channel'],
                        'calibrated_temp': reading['calibrated_temp'],
                        'unit': reading['unit']
                    }
                    if include_raw:
                        row['raw_temp'] = reading['temperature']
                    
                    writer.writerow(row)
            
            print(f"[TextLogger] Generated CSV export: {export_filename} ({len(readings)} records)")
            return str(export_path)
            
        except Exception as e:
            print(f"[TextLogger] Error generating CSV export: {e}")
            return None
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics for text files"""
        stats = {
            'raw_files': 0,
            'daily_files': 0,
            'compressed_files': 0,
            'total_size_mb': 0,
            'oldest_data': None,
            'newest_data': None
        }
        
        try:
            # Count raw files
            raw_files = list(self.raw_path.glob('*.txt'))
            stats['raw_files'] = len(raw_files)
            
            # Count daily files
            daily_files = list(self.daily_path.glob('*.txt'))
            stats['daily_files'] = len(daily_files)
            
            # Count compressed files
            compressed_files = list(self.compressed_path.glob('*.txt.gz'))
            stats['compressed_files'] = len(compressed_files)
            
            # Calculate total size
            total_size = 0
            for file_list in [raw_files, daily_files, compressed_files]:
                for file_path in file_list:
                    total_size += file_path.stat().st_size
            
            stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            # Find oldest and newest data
            all_files = raw_files + daily_files
            if all_files:
                dates = []
                for file_path in all_files:
                    try:
                        if '_' in file_path.stem:  # Raw file format
                            date_str = file_path.stem.split('_')[0]
                        else:  # Daily file format
                            date_str = file_path.stem
                        dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
                    except ValueError:
                        continue
                
                if dates:
                    stats['oldest_data'] = min(dates).isoformat()
                    stats['newest_data'] = max(dates).isoformat()
        
        except Exception as e:
            print(f"[TextLogger] Error getting storage stats: {e}")
        
        return stats
    
    def close(self):
        """Close any open file handles"""
        with self._lock:
            if self._current_raw_file:
                self._current_raw_file.close()
                self._current_raw_file = None

# Global instance
text_file_logger = TextFileLogger()