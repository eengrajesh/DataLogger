"""
Comprehensive Notification System for DataLogger
Handles email alerts for critical system events and monitoring
"""

import smtplib
import ssl
import json
import os
import time
import threading
import subprocess
import socket
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass
from enum import Enum
import queue

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning" 
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class Alert:
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime
    data: Dict[str, Any] = None
    sent: bool = False
    retry_count: int = 0

class ConnectivityMonitor:
    """Monitor internet and board connectivity"""
    
    def __init__(self):
        self.internet_connected = True
        self.board_connected = False
        self.last_internet_check = datetime.now()
        self.last_board_check = datetime.now()
        self.board_check_failures = 0
        self.internet_check_failures = 0
        
    def check_internet_connectivity(self) -> bool:
        """Check if internet is available"""
        try:
            # Try multiple reliable endpoints
            test_urls = [
                "8.8.8.8",      # Google DNS
                "1.1.1.1",      # Cloudflare DNS
                "208.67.222.222" # OpenDNS
            ]
            
            for url in test_urls:
                try:
                    socket.create_connection((url, 53), timeout=5)
                    self.internet_check_failures = 0
                    return True
                except (socket.timeout, socket.error):
                    continue
            
            self.internet_check_failures += 1
            return False
            
        except Exception as e:
            print(f"[ConnectivityMonitor] Internet check error: {e}")
            self.internet_check_failures += 1
            return False
    
    def check_board_connectivity(self) -> bool:
        """Check if SMTC board is connected"""
        try:
            from data_logger import daq
            
            # Try to get board info
            board_info = daq.get_board_info()
            if board_info and 'board_info' in board_info:
                self.board_check_failures = 0
                return True
            else:
                self.board_check_failures += 1
                return False
                
        except Exception as e:
            print(f"[ConnectivityMonitor] Board check error: {e}")
            self.board_check_failures += 1
            return False
    
    def get_connectivity_status(self) -> Dict[str, Any]:
        """Get current connectivity status"""
        internet_now = self.check_internet_connectivity()
        board_now = self.check_board_connectivity()
        
        # Detect state changes
        internet_changed = internet_now != self.internet_connected
        board_changed = board_now != self.board_connected
        
        status = {
            'internet': {
                'connected': internet_now,
                'changed': internet_changed,
                'was_connected': self.internet_connected,
                'failures': self.internet_check_failures,
                'last_check': self.last_internet_check.isoformat()
            },
            'board': {
                'connected': board_now,
                'changed': board_changed,
                'was_connected': self.board_connected,
                'failures': self.board_check_failures,
                'last_check': self.last_board_check.isoformat()
            }
        }
        
        # Update state
        self.internet_connected = internet_now
        self.board_connected = board_now
        self.last_internet_check = datetime.now()
        self.last_board_check = datetime.now()
        
        return status

class EmailNotificationSystem:
    """Comprehensive email notification system"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'email_config.json')
        
        self.config_path = config_path
        self.config = self.load_config()
        self.connectivity = ConnectivityMonitor()
        self.alert_queue = queue.Queue()
        self.sent_alerts = []  # Track sent alerts to avoid duplicates
        self.is_running = False
        self.worker_thread = None
        
        # Alert thresholds
        self.temp_warning_threshold = 70
        self.temp_critical_threshold = 80
        self.disk_warning_threshold = 85
        self.disk_critical_threshold = 95
        
        # State tracking
        self.last_cpu_temp = None
        self.consecutive_temp_warnings = 0
        self.last_disk_usage = None
        
    def load_config(self) -> Dict[str, Any]:
        """Load email configuration from file"""
        default_config = {
            "enabled": False,
            "smtp": {
                "server": "smtp.gmail.com",
                "port": 587,
                "use_tls": True,
                "username": "",
                "password": ""
            },
            "recipients": {
                "critical": [],
                "warning": [],
                "info": [],
                "reports": []
            },
            "alerts": {
                "cpu_temperature": True,
                "board_disconnect": True,
                "internet_disconnect": True,
                "logging_stopped": True,
                "disk_space": True,
                "power_events": True
            },
            "reports": {
                "daily_summary": False,
                "weekly_report": False,
                "daily_time": "08:00",
                "weekly_day": "monday"
            },
            "rate_limiting": {
                "max_alerts_per_hour": 10,
                "duplicate_suppression_minutes": 30
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
            return default_config
        except Exception as e:
            print(f"[EmailNotifier] Config load error: {e}")
            return default_config
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"[EmailNotifier] Config save error: {e}")
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update email configuration"""
        self.config.update(new_config)
        self.save_config()
    
    def create_alert(self, level: AlertLevel, title: str, message: str, 
                    data: Dict[str, Any] = None) -> Alert:
        """Create a new alert"""
        alert = Alert(
            level=level,
            title=title,
            message=message,
            timestamp=datetime.now(),
            data=data or {}
        )
        
        # Check for duplicate suppression
        if not self.is_duplicate_alert(alert):
            self.alert_queue.put(alert)
            print(f"[EmailNotifier] Alert queued: {level.value.upper()} - {title}")
        
        return alert
    
    def is_duplicate_alert(self, alert: Alert) -> bool:
        """Check if this is a duplicate alert within suppression window"""
        suppression_minutes = self.config['rate_limiting']['duplicate_suppression_minutes']
        cutoff_time = datetime.now() - timedelta(minutes=suppression_minutes)
        
        for sent_alert in self.sent_alerts:
            if (sent_alert.title == alert.title and 
                sent_alert.timestamp > cutoff_time):
                return True
        
        return False
    
    def send_email(self, alert: Alert) -> bool:
        """Send email for the given alert"""
        if not self.config['enabled']:
            print(f"[EmailNotifier] Email disabled, skipping: {alert.title}")
            return False
        
        try:
            # Get recipients based on alert level
            recipients = self.get_recipients_for_level(alert.level)
            if not recipients:
                print(f"[EmailNotifier] No recipients for {alert.level.value} alerts")
                return False
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[ENERTHERM] {alert.level.value.upper()}: {alert.title}"
            msg['From'] = self.config['smtp']['username']
            msg['To'] = ', '.join(recipients)
            
            # Create HTML content
            html_content = self.create_html_email(alert)
            msg.attach(MIMEText(html_content, 'html'))
            
            # Create plain text version
            text_content = self.create_text_email(alert)
            msg.attach(MIMEText(text_content, 'plain'))
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.config['smtp']['server'], self.config['smtp']['port']) as server:
                if self.config['smtp']['use_tls']:
                    server.starttls(context=context)
                
                server.login(self.config['smtp']['username'], self.config['smtp']['password'])
                server.send_message(msg)
            
            print(f"[EmailNotifier] Email sent successfully: {alert.title}")
            alert.sent = True
            self.sent_alerts.append(alert)
            return True
            
        except Exception as e:
            print(f"[EmailNotifier] Email send error: {e}")
            alert.retry_count += 1
            return False
    
    def get_recipients_for_level(self, level: AlertLevel) -> List[str]:
        """Get email recipients for the given alert level"""
        recipients = set()
        
        if level == AlertLevel.EMERGENCY or level == AlertLevel.CRITICAL:
            recipients.update(self.config['recipients']['critical'])
            recipients.update(self.config['recipients']['warning'])
        elif level == AlertLevel.WARNING:
            recipients.update(self.config['recipients']['warning'])
        elif level == AlertLevel.INFO:
            recipients.update(self.config['recipients']['info'])
        
        return list(recipients)
    
    def create_html_email(self, alert: Alert) -> str:
        """Create HTML email content"""
        level_colors = {
            AlertLevel.INFO: '#3b82f6',
            AlertLevel.WARNING: '#f59e0b', 
            AlertLevel.CRITICAL: '#ef4444',
            AlertLevel.EMERGENCY: '#dc2626'
        }
        
        color = level_colors.get(alert.level, '#6b7280')
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <!-- Header -->
                <div style="background: {color}; color: white; padding: 20px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">ENERTHERM ENGINEERING</h1>
                    <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Temperature Data Logger Alert</p>
                </div>
                
                <!-- Alert Content -->
                <div style="padding: 30px;">
                    <div style="border-left: 4px solid {color}; padding-left: 20px; margin-bottom: 20px;">
                        <h2 style="margin: 0 0 10px 0; color: {color}; font-size: 20px;">{alert.level.value.upper()}: {alert.title}</h2>
                        <p style="margin: 0; color: #666; font-size: 14px;">{alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    <div style="background: #f9fafb; padding: 20px; border-radius: 6px; margin-bottom: 20px;">
                        <p style="margin: 0; font-size: 16px; line-height: 1.5;">{alert.message}</p>
                    </div>
                    
                    {self.create_alert_data_html(alert)}
                    
                    <!-- Footer -->
                    <div style="border-top: 1px solid #e5e7eb; padding-top: 20px; margin-top: 20px; text-align: center;">
                        <p style="margin: 0; color: #9ca3af; font-size: 12px;">
                            Generated by Enertherm Engineering DataLogger System<br>
                            Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def create_alert_data_html(self, alert: Alert) -> str:
        """Create HTML for alert data"""
        if not alert.data:
            return ""
        
        html = '<div style="margin: 20px 0;"><h3 style="color: #374151; font-size: 16px; margin-bottom: 10px;">Additional Information:</h3><ul style="margin: 0; padding-left: 20px;">'
        
        for key, value in alert.data.items():
            html += f'<li style="margin-bottom: 5px;"><strong>{key}:</strong> {value}</li>'
        
        html += '</ul></div>'
        return html
    
    def create_text_email(self, alert: Alert) -> str:
        """Create plain text email content"""
        text = f"""
ENERTHERM ENGINEERING - Temperature Data Logger Alert

{alert.level.value.upper()}: {alert.title}
Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

{alert.message}
"""
        
        if alert.data:
            text += "\nAdditional Information:\n"
            for key, value in alert.data.items():
                text += f"- {key}: {value}\n"
        
        text += f"\nGenerated by DataLogger System at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return text
    
    def check_cpu_temperature(self):
        """Check CPU temperature and create alerts"""
        if not self.config['alerts']['cpu_temperature']:
            return
        
        try:
            from data_logger import get_cpu_temperature
            cpu_data = get_cpu_temperature()
            temp = cpu_data.get('cpu_temp', -1)
            
            if temp <= 0:
                return  # Invalid reading
            
            self.last_cpu_temp = temp
            
            if temp >= self.temp_critical_threshold:
                self.create_alert(
                    AlertLevel.CRITICAL,
                    "Critical CPU Temperature",
                    f"Board CPU temperature is critically high at {temp:.1f}°C. Immediate action required to prevent damage.",
                    {
                        "Current Temperature": f"{temp:.1f}°C",
                        "Critical Threshold": f"{self.temp_critical_threshold}°C",
                        "Recommended Actions": "Check cooling, reduce load, or shutdown system"
                    }
                )
                self.consecutive_temp_warnings += 1
                
            elif temp >= self.temp_warning_threshold:
                self.consecutive_temp_warnings += 1
                
                # Only send warning after 3 consecutive high readings
                if self.consecutive_temp_warnings >= 3:
                    self.create_alert(
                        AlertLevel.WARNING,
                        "High CPU Temperature",
                        f"Board CPU temperature is elevated at {temp:.1f}°C. Monitor closely.",
                        {
                            "Current Temperature": f"{temp:.1f}°C",
                            "Warning Threshold": f"{self.temp_warning_threshold}°C",
                            "Consecutive Warnings": str(self.consecutive_temp_warnings)
                        }
                    )
            else:
                # Reset counter when temperature is normal
                self.consecutive_temp_warnings = 0
                
        except Exception as e:
            print(f"[EmailNotifier] CPU temp check error: {e}")
    
    def check_connectivity(self):
        """Check connectivity and create alerts"""
        status = self.connectivity.get_connectivity_status()
        
        # Board disconnect alerts
        if (self.config['alerts']['board_disconnect'] and 
            status['board']['changed'] and 
            not status['board']['connected']):
            
            self.create_alert(
                AlertLevel.CRITICAL,
                "SMTC Board Disconnected",
                "The thermocouple measurement board has been disconnected. Temperature logging will stop.",
                {
                    "Disconnect Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "Previous State": "Connected" if status['board']['was_connected'] else "Disconnected",
                    "Failure Count": str(status['board']['failures'])
                }
            )
        
        # Board reconnect notification
        if (status['board']['changed'] and 
            status['board']['connected'] and 
            not status['board']['was_connected']):
            
            self.create_alert(
                AlertLevel.INFO,
                "SMTC Board Reconnected",
                "The thermocouple measurement board has been reconnected. Temperature logging can resume.",
                {
                    "Reconnect Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            )
        
        # Internet disconnect alerts
        if (self.config['alerts']['internet_disconnect'] and 
            status['internet']['changed'] and 
            not status['internet']['connected']):
            
            # Store this alert for later sending when internet returns
            alert = Alert(
                AlertLevel.WARNING,
                "Internet Connection Lost",
                "Internet connectivity has been lost. Email alerts will be queued until connection is restored.",
                {
                    "Disconnect Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "Failure Count": str(status['internet']['failures'])
                },
                timestamp=datetime.now()
            )
            
            # Save to persistent queue (file-based)
            self.save_alert_to_file(alert)
            print("[EmailNotifier] Internet disconnected, alert saved for later")
        
        # Internet reconnect - send queued alerts
        if (status['internet']['changed'] and 
            status['internet']['connected'] and 
            not status['internet']['was_connected']):
            
            self.create_alert(
                AlertLevel.INFO,
                "Internet Connection Restored", 
                "Internet connectivity has been restored. Sending queued alerts.",
                {
                    "Reconnect Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            
            # Load and send queued alerts
            self.process_queued_alerts()
    
    def save_alert_to_file(self, alert: Alert):
        """Save alert to file for later sending"""
        try:
            alert_file = os.path.join(os.path.dirname(__file__), 'queued_alerts.json')
            
            alerts = []
            if os.path.exists(alert_file):
                with open(alert_file, 'r') as f:
                    alerts = json.load(f)
            
            alert_dict = {
                'level': alert.level.value,
                'title': alert.title,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'data': alert.data
            }
            
            alerts.append(alert_dict)
            
            with open(alert_file, 'w') as f:
                json.dump(alerts, f, indent=2)
                
        except Exception as e:
            print(f"[EmailNotifier] Error saving alert to file: {e}")
    
    def process_queued_alerts(self):
        """Process alerts saved during internet outage"""
        try:
            alert_file = os.path.join(os.path.dirname(__file__), 'queued_alerts.json')
            
            if not os.path.exists(alert_file):
                return
            
            with open(alert_file, 'r') as f:
                queued_alerts = json.load(f)
            
            for alert_dict in queued_alerts:
                alert = Alert(
                    level=AlertLevel(alert_dict['level']),
                    title=alert_dict['title'],
                    message=alert_dict['message'],
                    timestamp=datetime.fromisoformat(alert_dict['timestamp']),
                    data=alert_dict.get('data', {})
                )
                self.alert_queue.put(alert)
            
            # Clear the file
            os.remove(alert_file)
            print(f"[EmailNotifier] Processed {len(queued_alerts)} queued alerts")
            
        except Exception as e:
            print(f"[EmailNotifier] Error processing queued alerts: {e}")
    
    def check_disk_space(self):
        """Check disk space and create alerts"""
        if not self.config['alerts']['disk_space']:
            return
        
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            usage_percent = (used / total) * 100
            
            self.last_disk_usage = usage_percent
            
            if usage_percent >= self.disk_critical_threshold:
                self.create_alert(
                    AlertLevel.CRITICAL,
                    "Critical Disk Space",
                    f"Disk usage is critically high at {usage_percent:.1f}%. System may become unstable.",
                    {
                        "Disk Usage": f"{usage_percent:.1f}%",
                        "Free Space": f"{free // (1024**3):.1f} GB",
                        "Total Space": f"{total // (1024**3):.1f} GB"
                    }
                )
            elif usage_percent >= self.disk_warning_threshold:
                self.create_alert(
                    AlertLevel.WARNING,
                    "Low Disk Space",
                    f"Disk usage is high at {usage_percent:.1f}%. Consider cleaning up old files.",
                    {
                        "Disk Usage": f"{usage_percent:.1f}%",
                        "Free Space": f"{free // (1024**3):.1f} GB"
                    }
                )
                
        except Exception as e:
            print(f"[EmailNotifier] Disk space check error: {e}")
    
    def monitor_logging_status(self):
        """Monitor if logging is running"""
        if not self.config['alerts']['logging_stopped']:
            return
        
        try:
            from data_logger import logging_thread
            
            if logging_thread is None or not logging_thread.is_alive():
                self.create_alert(
                    AlertLevel.WARNING,
                    "Temperature Logging Stopped",
                    "Temperature data logging has stopped. No new data will be collected until logging is restarted.",
                    {
                        "Stop Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "Action Required": "Check system and restart logging"
                    }
                )
        except Exception as e:
            print(f"[EmailNotifier] Logging status check error: {e}")
    
    def worker_loop(self):
        """Main worker loop for processing alerts"""
        print("[EmailNotifier] Worker thread started")
        
        last_connectivity_check = datetime.now()
        last_temp_check = datetime.now()
        last_disk_check = datetime.now()
        last_logging_check = datetime.now()
        
        while self.is_running:
            try:
                now = datetime.now()
                
                # Process queued alerts
                try:
                    alert = self.alert_queue.get(timeout=1)
                    self.send_email(alert)
                except queue.Empty:
                    pass
                
                # Periodic checks
                if (now - last_connectivity_check).seconds >= 30:  # Every 30 seconds
                    self.check_connectivity()
                    last_connectivity_check = now
                
                if (now - last_temp_check).seconds >= 60:  # Every minute
                    self.check_cpu_temperature()
                    last_temp_check = now
                
                if (now - last_disk_check).seconds >= 300:  # Every 5 minutes
                    self.check_disk_space()
                    last_disk_check = now
                
                if (now - last_logging_check).seconds >= 120:  # Every 2 minutes
                    self.monitor_logging_status()
                    last_logging_check = now
                
            except Exception as e:
                print(f"[EmailNotifier] Worker loop error: {e}")
                time.sleep(5)
    
    def start(self):
        """Start the notification system"""
        if self.is_running:
            return False
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self.worker_loop, daemon=True)
        self.worker_thread.start()
        print("[EmailNotifier] Notification system started")
        return True
    
    def stop(self):
        """Stop the notification system"""
        self.is_running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        print("[EmailNotifier] Notification system stopped")
    
    def test_email(self, recipient: str = None) -> bool:
        """Send a test email"""
        test_recipients = [recipient] if recipient else self.config['recipients']['info']
        
        if not test_recipients:
            return False
        
        alert = Alert(
            level=AlertLevel.INFO,
            title="Email System Test",
            message="This is a test email to verify the notification system is working correctly.",
            timestamp=datetime.now(),
            data={
                "System Status": "Operational",
                "Test Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        )
        
        return self.send_email(alert)

# Global instance
notification_system = EmailNotificationSystem()