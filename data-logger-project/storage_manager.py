import os
import platform
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime

class StorageDevice:
    def __init__(self, name: str, path: str, type: str, available: bool, total_space: int, free_space: int):
        self.name = name
        self.path = path
        self.type = type  # 'local', 'sd', 'usb'
        self.available = available
        self.total_space = total_space
        self.free_space = free_space
        self.used_space = total_space - free_space if available else 0
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'path': self.path,
            'type': self.type,
            'available': self.available,
            'total_space_gb': round(self.total_space / (1024**3), 2) if self.available else 0,
            'free_space_gb': round(self.free_space / (1024**3), 2) if self.available else 0,
            'used_space_gb': round(self.used_space / (1024**3), 2) if self.available else 0,
            'usage_percent': round((self.used_space / self.total_space) * 100, 1) if self.available and self.total_space > 0 else 0
        }

class StorageManager:
    def __init__(self):
        self.is_windows = platform.system() == 'Windows'
        self.local_path = Path('./data')
        self.ensure_local_storage()
        
        # Default paths for Raspberry Pi
        self.sd_mount_points = ['/media/sd', '/mnt/sd', '/media/pi']
        self.usb_mount_points = ['/media/usb', '/mnt/usb', '/media/pi']
        
        # For Windows development - simulate removable storage
        if self.is_windows:
            self.sd_mount_points = [Path('./simulated_sd')]
            self.usb_mount_points = [Path('./simulated_usb')]
            self._create_simulated_storage()
    
    def ensure_local_storage(self):
        self.local_path.mkdir(parents=True, exist_ok=True)
    
    def _create_simulated_storage(self):
        """Create simulated storage directories for Windows development"""
        if self.is_windows:
            for path in self.sd_mount_points + self.usb_mount_points:
                Path(path).mkdir(parents=True, exist_ok=True)
    
    def scan_storage_devices(self) -> List[StorageDevice]:
        devices = []
        
        # Always add local storage
        local_stat = shutil.disk_usage(self.local_path)
        devices.append(StorageDevice(
            name="Local Storage",
            path=str(self.local_path.absolute()),
            type="local",
            available=True,
            total_space=local_stat.total,
            free_space=local_stat.free
        ))
        
        # Check SD card mount points
        for mount_point in self.sd_mount_points:
            device = self._check_mount_point(mount_point, "sd")
            if device:
                devices.append(device)
        
        # Check USB mount points
        for mount_point in self.usb_mount_points:
            device = self._check_mount_point(mount_point, "usb")
            if device:
                devices.append(device)
        
        return devices
    
    def _check_mount_point(self, mount_point: Path, device_type: str) -> Optional[StorageDevice]:
        mount_path = Path(mount_point)
        
        if mount_path.exists() and mount_path.is_dir():
            try:
                # Check if it's actually mounted (on Linux)
                if not self.is_windows:
                    # Check if mount point has different device than parent
                    if mount_path.stat().st_dev == mount_path.parent.stat().st_dev:
                        return None  # Not a separate mount
                
                stat = shutil.disk_usage(mount_path)
                
                # Only consider it available if it has reasonable space
                if stat.total > 1024 * 1024:  # At least 1MB
                    name = f"SD Card" if device_type == "sd" else f"USB Storage"
                    return StorageDevice(
                        name=name,
                        path=str(mount_path.absolute()),
                        type=device_type,
                        available=True,
                        total_space=stat.total,
                        free_space=stat.free
                    )
            except Exception as e:
                print(f"Error checking mount point {mount_path}: {e}")
        
        return None
    
    def get_active_storage(self) -> StorageDevice:
        """Get the currently active storage device based on config"""
        from config import config
        
        storage_type = config.get('storage.primary', 'local')
        devices = self.scan_storage_devices()
        
        # Find the configured storage
        for device in devices:
            if device.type == storage_type and device.available:
                return device
        
        # Fallback to local storage
        return devices[0]  # Local storage is always first
    
    def set_active_storage(self, storage_type: str) -> bool:
        """Set the active storage device"""
        from config import config
        
        devices = self.scan_storage_devices()
        for device in devices:
            if device.type == storage_type and device.available:
                config.set('storage.primary', storage_type)
                return True
        return False
    
    def export_data_to_storage(self, data: List[Dict], filename: str, storage_type: str = None) -> str:
        """Export data to specified storage device"""
        if storage_type:
            devices = self.scan_storage_devices()
            device = next((d for d in devices if d.type == storage_type and d.available), None)
            if not device:
                raise ValueError(f"Storage device '{storage_type}' not available")
            export_path = Path(device.path)
        else:
            device = self.get_active_storage()
            export_path = Path(device.path)
        
        # Create exports directory
        export_dir = export_path / 'exports'
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'datalog_{timestamp}.json'
        
        file_path = export_dir / filename
        
        # Save data
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return str(file_path)
    
    def list_exported_files(self, storage_type: str = None) -> List[Dict]:
        """List exported files from storage"""
        if storage_type:
            devices = self.scan_storage_devices()
            device = next((d for d in devices if d.type == storage_type and d.available), None)
            if not device:
                return []
            export_path = Path(device.path) / 'exports'
        else:
            device = self.get_active_storage()
            export_path = Path(device.path) / 'exports'
        
        if not export_path.exists():
            return []
        
        files = []
        for file in export_path.glob('*'):
            if file.is_file():
                stat = file.stat()
                files.append({
                    'name': file.name,
                    'path': str(file),
                    'size_kb': round(stat.st_size / 1024, 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return sorted(files, key=lambda x: x['modified'], reverse=True)
    
    def get_storage_status(self) -> Dict:
        """Get comprehensive storage status"""
        devices = self.scan_storage_devices()
        active_storage = self.get_active_storage()
        
        return {
            'devices': [d.to_dict() for d in devices],
            'active_device': active_storage.to_dict(),
            'total_devices': len(devices),
            'available_devices': sum(1 for d in devices if d.available)
        }