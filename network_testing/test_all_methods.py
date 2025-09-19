#!/usr/bin/env python3
"""
Comprehensive Network Testing Script for DataLogger
Run each test method independently and generate results
"""

import os
import sys
import time
import json
import socket
import requests
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class NetworkMethodTester:
    def __init__(self, pi_ip: str = None):
        self.pi_ip = pi_ip
        self.results = {
            "test_date": datetime.now().isoformat(),
            "pi_ip": pi_ip,
            "methods": {}
        }
        
    def test_local_network(self) -> Dict[str, Any]:
        """Test 1: Local Network Access"""
        print("\n" + "="*50)
        print("Testing LOCAL NETWORK ACCESS")
        print("="*50)
        
        if not self.pi_ip:
            self.pi_ip = input("Enter Pi5 IP address: ")
        
        result = {
            "method_name": "Local Network",
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Test 1: Ping
        print(f"\n[1] Pinging {self.pi_ip}...")
        try:
            cmd = ["ping", "-n" if os.name == 'nt' else "-c", "4", self.pi_ip]
            ping_result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            result["tests"]["ping"] = {
                "success": ping_result.returncode == 0,
                "output": ping_result.stdout[:200]
            }
            print("✓ Ping successful" if ping_result.returncode == 0 else "✗ Ping failed")
        except Exception as e:
            result["tests"]["ping"] = {"success": False, "error": str(e)}
            print(f"✗ Error: {e}")
        
        # Test 2: HTTP API
        print(f"\n[2] Testing HTTP API...")
        try:
            response = requests.get(f"http://{self.pi_ip}:8080/api/board_info", timeout=5)
            result["tests"]["http_api"] = {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
            print(f"✓ API accessible (Status: {response.status_code})")
        except Exception as e:
            result["tests"]["http_api"] = {"success": False, "error": str(e)}
            print(f"✗ API Error: {e}")
        
        # Test 3: SSH Port
        print(f"\n[3] Testing SSH port 22...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            ssh_result = sock.connect_ex((self.pi_ip, 22))
            sock.close()
            result["tests"]["ssh_port"] = {"success": ssh_result == 0, "port_open": ssh_result == 0}
            print("✓ SSH port open" if ssh_result == 0 else "✗ SSH port closed")
        except Exception as e:
            result["tests"]["ssh_port"] = {"success": False, "error": str(e)}
            print(f"✗ SSH Error: {e}")
        
        # Calculate score
        passed = sum(1 for t in result["tests"].values() if t.get("success", False))
        total = len(result["tests"])
        result["score"] = (passed / total * 100) if total > 0 else 0
        result["summary"] = f"Passed {passed}/{total} tests"
        
        print(f"\n📊 Local Network Score: {result['score']:.0f}%")
        return result
    
    def test_tailscale(self) -> Dict[str, Any]:
        """Test 2: Tailscale VPN"""
        print("\n" + "="*50)
        print("Testing TAILSCALE VPN")
        print("="*50)
        
        result = {
            "method_name": "Tailscale VPN",
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        print("\nChecking if Tailscale is installed...")
        
        # Check Tailscale installation
        try:
            ts_status = subprocess.run(["tailscale", "status"], capture_output=True, text=True)
            if ts_status.returncode == 0:
                result["tests"]["installed"] = {"success": True}
                print("✓ Tailscale is installed")
                
                # Parse status for Pi device
                lines = ts_status.stdout.split('\n')
                for line in lines:
                    if 'datalogger' in line.lower() or 'pi' in line.lower():
                        parts = line.split()
                        if parts and parts[0].startswith('100.'):
                            tailscale_ip = parts[0]
                            print(f"✓ Found Pi at Tailscale IP: {tailscale_ip}")
                            
                            # Test connection
                            try:
                                response = requests.get(f"http://{tailscale_ip}:8080/api/board_info", timeout=5)
                                result["tests"]["connection"] = {
                                    "success": response.status_code == 200,
                                    "tailscale_ip": tailscale_ip
                                }
                                print(f"✓ Connected via Tailscale")
                            except Exception as e:
                                result["tests"]["connection"] = {"success": False, "error": str(e)}
                                print(f"✗ Connection failed: {e}")
            else:
                result["tests"]["installed"] = {"success": False, "message": "Tailscale not installed"}
                print("✗ Tailscale not installed. Install from: https://tailscale.com/download")
        except FileNotFoundError:
            result["tests"]["installed"] = {"success": False, "message": "Tailscale not found"}
            print("✗ Tailscale not found in PATH")
        except Exception as e:
            result["tests"]["installed"] = {"success": False, "error": str(e)}
            print(f"✗ Error: {e}")
        
        # Calculate score
        if result["tests"].get("installed", {}).get("success"):
            result["score"] = 100 if result["tests"].get("connection", {}).get("success") else 50
        else:
            result["score"] = 0
            
        print(f"\n📊 Tailscale Score: {result['score']:.0f}%")
        return result
    
    def test_cloudflare_tunnel(self) -> Dict[str, Any]:
        """Test 3: Cloudflare Tunnel"""
        print("\n" + "="*50)
        print("Testing CLOUDFLARE TUNNEL")
        print("="*50)
        
        result = {
            "method_name": "Cloudflare Tunnel",
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        print("\nTo test Cloudflare Tunnel:")
        print("1. Run on Pi5: ./cloudflared-linux-arm64 tunnel --url http://localhost:8080")
        print("2. You'll get a URL like: https://random-name.trycloudflare.com")
        
        tunnel_url = input("\nEnter Cloudflare tunnel URL (or 'skip'): ").strip()
        
        if tunnel_url.lower() != 'skip' and tunnel_url.startswith('http'):
            print(f"\nTesting tunnel: {tunnel_url}")
            try:
                response = requests.get(f"{tunnel_url}/api/board_info", timeout=10)
                result["tests"]["tunnel"] = {
                    "success": response.status_code == 200,
                    "url": tunnel_url,
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "publicly_accessible": True
                }
                print(f"✓ Tunnel working! Response time: {response.elapsed.total_seconds()*1000:.0f}ms")
                result["score"] = 100
            except Exception as e:
                result["tests"]["tunnel"] = {"success": False, "error": str(e)}
                print(f"✗ Tunnel error: {e}")
                result["score"] = 0
        else:
            result["tests"]["tunnel"] = {"success": False, "skipped": True}
            result["score"] = 0
            print("⚠ Skipped Cloudflare tunnel test")
        
        print(f"\n📊 Cloudflare Score: {result['score']:.0f}%")
        return result
    
    def test_mqtt(self) -> Dict[str, Any]:
        """Test 4: MQTT Broker"""
        print("\n" + "="*50)
        print("Testing MQTT BROKER")
        print("="*50)
        
        result = {
            "method_name": "MQTT Broker",
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        try:
            import paho.mqtt.client as mqtt
            
            print("\nTesting connection to test.mosquitto.org...")
            
            connected = False
            def on_connect(client, userdata, flags, rc):
                nonlocal connected
                connected = (rc == 0)
            
            client = mqtt.Client()
            client.on_connect = on_connect
            
            try:
                client.connect("test.mosquitto.org", 1883, 60)
                client.loop_start()
                time.sleep(3)  # Wait for connection
                client.loop_stop()
                
                result["tests"]["broker_connection"] = {
                    "success": connected,
                    "broker": "test.mosquitto.org"
                }
                
                if connected:
                    print("✓ Connected to MQTT broker")
                    result["score"] = 100
                else:
                    print("✗ Failed to connect to MQTT broker")
                    result["score"] = 0
                    
            except Exception as e:
                result["tests"]["broker_connection"] = {"success": False, "error": str(e)}
                print(f"✗ MQTT Error: {e}")
                result["score"] = 0
                
        except ImportError:
            result["tests"]["broker_connection"] = {
                "success": False, 
                "error": "paho-mqtt not installed. Run: pip install paho-mqtt"
            }
            print("✗ paho-mqtt not installed")
            result["score"] = 0
        
        print(f"\n📊 MQTT Score: {result['score']:.0f}%")
        return result
    
    def test_telegram_bot(self) -> Dict[str, Any]:
        """Test 5: Telegram Bot"""
        print("\n" + "="*50)
        print("Testing TELEGRAM BOT")
        print("="*50)
        
        result = {
            "method_name": "Telegram Bot",
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        print("\nTo test Telegram Bot:")
        print("1. Create bot with @BotFather")
        print("2. Get your bot token")
        
        token = input("\nEnter bot token (or 'skip'): ").strip()
        
        if token.lower() != 'skip' and len(token) > 20:
            print("\nTesting Telegram API...")
            try:
                response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5)
                if response.status_code == 200:
                    bot_data = response.json()
                    result["tests"]["api_connection"] = {
                        "success": True,
                        "bot_username": bot_data.get("result", {}).get("username", "Unknown"),
                        "bot_id": bot_data.get("result", {}).get("id")
                    }
                    print(f"✓ Bot connected: @{bot_data.get('result', {}).get('username', 'Unknown')}")
                    result["score"] = 100
                else:
                    result["tests"]["api_connection"] = {"success": False, "status": response.status_code}
                    print(f"✗ Invalid token or API error")
                    result["score"] = 0
            except Exception as e:
                result["tests"]["api_connection"] = {"success": False, "error": str(e)}
                print(f"✗ Telegram API error: {e}")
                result["score"] = 0
        else:
            result["tests"]["api_connection"] = {"success": False, "skipped": True}
            result["score"] = 0
            print("⚠ Skipped Telegram bot test")
        
        print(f"\n📊 Telegram Score: {result['score']:.0f}%")
        return result
    
    def test_thingspeak(self) -> Dict[str, Any]:
        """Test 6: ThingSpeak Cloud Broker"""
        print("\n" + "="*50)
        print("Testing THINGSPEAK")
        print("="*50)
        
        result = {
            "method_name": "ThingSpeak",
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        print("\nTo test ThingSpeak:")
        print("1. Create account at thingspeak.com")
        print("2. Create a channel")
        print("3. Get Write API Key")
        
        api_key = input("\nEnter ThingSpeak Write API Key (or 'skip'): ").strip()
        
        if api_key.lower() != 'skip' and len(api_key) > 10:
            print("\nTesting ThingSpeak API...")
            try:
                # Send test data
                test_data = {
                    'api_key': api_key,
                    'field1': 23.5,
                    'field2': 45.2
                }
                response = requests.post(
                    'https://api.thingspeak.com/update',
                    params=test_data,
                    timeout=10
                )
                
                if response.status_code == 200 and response.text != '0':
                    result["tests"]["data_upload"] = {
                        "success": True,
                        "entry_id": response.text
                    }
                    print(f"✓ Data uploaded successfully! Entry ID: {response.text}")
                    result["score"] = 100
                else:
                    result["tests"]["data_upload"] = {"success": False, "response": response.text}
                    print(f"✗ Upload failed")
                    result["score"] = 0
                    
            except Exception as e:
                result["tests"]["data_upload"] = {"success": False, "error": str(e)}
                print(f"✗ ThingSpeak error: {e}")
                result["score"] = 0
        else:
            result["tests"]["data_upload"] = {"success": False, "skipped": True}
            result["score"] = 0
            print("⚠ Skipped ThingSpeak test")
        
        print(f"\n📊 ThingSpeak Score: {result['score']:.0f}%")
        return result
    
    def run_all_tests(self):
        """Run all network tests"""
        print("""
        ╔════════════════════════════════════════════════════════╗
        ║     DataLogger Network Testing Suite                    ║
        ║     Testing all connectivity methods                    ║
        ╚════════════════════════════════════════════════════════╝
        """)
        
        # Run each test
        test_methods = [
            ("local_network", self.test_local_network),
            ("tailscale", self.test_tailscale),
            ("cloudflare", self.test_cloudflare_tunnel),
            ("mqtt", self.test_mqtt),
            ("telegram", self.test_telegram_bot),
            ("thingspeak", self.test_thingspeak)
        ]
        
        for method_id, test_func in test_methods:
            try:
                self.results["methods"][method_id] = test_func()
                time.sleep(1)  # Brief pause between tests
            except KeyboardInterrupt:
                print("\n\nTesting interrupted by user")
                break
            except Exception as e:
                print(f"\nError in {method_id}: {e}")
                self.results["methods"][method_id] = {
                    "error": str(e),
                    "score": 0
                }
        
        # Generate summary
        self.generate_summary()
        
        # Save results
        self.save_results()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*60)
        print("TESTING SUMMARY")
        print("="*60)
        
        print(f"\n{'Method':<20} {'Score':<10} {'Status':<20}")
        print("-"*50)
        
        for method_id, result in self.results["methods"].items():
            score = result.get("score", 0)
            status = "✓ Working" if score > 50 else "✗ Failed" if score == 0 else "⚠ Partial"
            method_name = result.get("method_name", method_id)
            print(f"{method_name:<20} {score:<10.0f} {status:<20}")
        
        # Best method
        if self.results["methods"]:
            best = max(self.results["methods"].items(), 
                      key=lambda x: x[1].get("score", 0))
            if best[1].get("score", 0) > 0:
                print(f"\n🏆 Best Method: {best[1].get('method_name')} (Score: {best[1].get('score', 0):.0f})")
        
        # Firewall-friendly methods
        firewall_friendly = ["tailscale", "cloudflare", "mqtt", "telegram", "thingspeak"]
        working_ff = [m for m in firewall_friendly 
                     if m in self.results["methods"] 
                     and self.results["methods"][m].get("score", 0) > 0]
        
        if working_ff:
            print(f"\n🔒 Firewall-Friendly Methods Working: {', '.join(working_ff)}")
    
    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"network_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        
        # Also create a summary report
        report_file = f"network_test_report_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write("DATALOGGER NETWORK TEST REPORT\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Pi IP: {self.pi_ip}\n")
            f.write("="*60 + "\n\n")
            
            for method_id, result in self.results["methods"].items():
                f.write(f"Method: {result.get('method_name', method_id)}\n")
                f.write(f"Score: {result.get('score', 0):.0f}/100\n")
                f.write(f"Tests: {json.dumps(result.get('tests', {}), indent=2)}\n")
                f.write("-"*40 + "\n\n")
        
        print(f"📄 Report saved to: {report_file}")

def main():
    if len(sys.argv) > 1:
        # Allow passing Pi IP as argument
        tester = NetworkMethodTester(sys.argv[1])
    else:
        tester = NetworkMethodTester()
    
    tester.run_all_tests()
    
    print("\n✅ Testing complete! Check the generated reports for details.")

if __name__ == "__main__":
    main()