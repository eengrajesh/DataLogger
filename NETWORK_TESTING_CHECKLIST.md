# 📋 DATALOGGER NETWORK CONNECTIVITY TESTING CHECKLIST

**Project:** Raspberry Pi DataLogger Network Access Testing  
**Date:** _______________  
**Tester:** _______________  
**Pi5 Location:** _______________  
**Network Type:** ☐ Home ☐ Office ☐ Industrial ☐ Secured/Restricted

---

## 🔧 PRE-TEST SETUP CHECKLIST

### Hardware Requirements:
- [ ] Raspberry Pi 5 powered on
- [ ] Sequent Microsystems 8-Thermocouple DAQ HAT connected
- [ ] Ethernet cable or WiFi configured
- [ ] MicroSD card with OS installed
- [ ] Power supply connected (5V/3A recommended)

### Software Requirements on Pi5:
- [ ] DataLogger application installed (`/home/pi/DataLogger`)
- [ ] Python 3.9+ installed
- [ ] Flask server configured (port 8080)
- [ ] SQLite database initialized
- [ ] Service running: `sudo systemctl status datalogger`

### Network Configuration:
- [ ] Pi5 IP address noted: ___.___.___.___ 
- [ ] Router access available: ☐ Yes ☐ No
- [ ] Firewall rules checked: ☐ Yes ☐ No
- [ ] Internet connection tested: ☐ Yes ☐ No

### Testing Computer Setup:
- [ ] Python 3.x installed
- [ ] `pip install requests paho-mqtt telegram-bot`
- [ ] Network testing scripts downloaded
- [ ] Same network as Pi5: ☐ Yes ☐ No

---

## 📝 METHOD 1: LOCAL NETWORK ACCESS (LAN)

### Configuration:
- Pi5 Local IP: ___.___.___.___
- Router Model: _______________
- Network Name: _______________

### Tests:
- [ ] **Ping Test**
  - Command: `ping [Pi5_IP] -c 4`
  - Success: ☐ Yes ☐ No
  - Avg Latency: _____ms
  
- [ ] **SSH Access**
  - Command: `ssh pi@[Pi5_IP]`
  - Port 22 Open: ☐ Yes ☐ No
  - Login Success: ☐ Yes ☐ No
  
- [ ] **Web Interface**
  - URL: `http://[Pi5_IP]:8080`
  - Page Loads: ☐ Yes ☐ No
  - Response Time: _____ms
  
- [ ] **API Test**
  - URL: `http://[Pi5_IP]:8080/api/board_info`
  - JSON Response: ☐ Yes ☐ No
  - Data Correct: ☐ Yes ☐ No

### Port Forwarding Setup (if needed):
- [ ] Router Admin Access: `http://192.168.1.1`
- [ ] External Port: _______ → Internal Port: 8080
- [ ] External SSH: _______ → Internal Port: 22
- [ ] DDNS Configured: ☐ Yes ☐ No
- [ ] DDNS URL: _______________

**Score: ___/10** | **Works Outside LAN: ☐ Yes ☐ No**

---

## 📝 METHOD 2: TAILSCALE VPN

### Installation on Pi5:
- [ ] Run: `curl -fsSL https://tailscale.com/install.sh | sh`
- [ ] Run: `sudo tailscale up`
- [ ] Auth URL visited: ☐ Yes ☐ No
- [ ] Device name: _______________
- [ ] Tailscale IP: 100.___.___.___ 

### Installation on Testing Computer:
- [ ] Tailscale downloaded from: https://tailscale.com/download
- [ ] Logged in with same account: ☐ Yes ☐ No
- [ ] Pi5 visible in network: ☐ Yes ☐ No

### Connection Tests:
- [ ] **Ping via Tailscale**
  - Command: `ping 100.x.x.x -c 4`
  - Success: ☐ Yes ☐ No
  - Latency: _____ms
  
- [ ] **Web Access**
  - URL: `http://100.x.x.x:8080`
  - Works: ☐ Yes ☐ No
  - From different network: ☐ Yes ☐ No
  
- [ ] **SSH via Tailscale**
  - Command: `ssh pi@100.x.x.x`
  - Works: ☐ Yes ☐ No

### Features Tested:
- [ ] Works behind NAT: ☐ Yes ☐ No
- [ ] Works on cellular: ☐ Yes ☐ No
- [ ] Works on public WiFi: ☐ Yes ☐ No
- [ ] Auto-reconnects: ☐ Yes ☐ No

**Score: ___/10** | **Firewall Friendly: ☐ Yes ☐ No**

---

## 📝 METHOD 3: CLOUDFLARE TUNNEL

### Setup on Pi5:
- [ ] Download cloudflared:
  ```bash
  wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
  chmod +x cloudflared-linux-arm64
  ```
- [ ] Run tunnel: `./cloudflared-linux-arm64 tunnel --url http://localhost:8080`
- [ ] Public URL received: https://_______________. trycloudflare.com
- [ ] URL copied/saved: ☐ Yes ☐ No

### Access Tests:
- [ ] **Public URL Access**
  - From local network: ☐ Works ☐ Fails
  - From cellular/4G: ☐ Works ☐ Fails
  - From different WiFi: ☐ Works ☐ Fails
  - Response time: _____ms
  
- [ ] **API Endpoints**
  - `/api/data/latest`: ☐ Works ☐ Fails
  - `/api/board_info`: ☐ Works ☐ Fails
  - `/api/data/live/1`: ☐ Works ☐ Fails
  
- [ ] **Persistent Tunnel Setup** (optional)
  - Service created: ☐ Yes ☐ No
  - Auto-starts on boot: ☐ Yes ☐ No
  - Config file path: _______________

### Security Tests:
- [ ] HTTPS enforced: ☐ Yes ☐ No
- [ ] No authentication required: ☐ Yes ☐ No (Note: Add auth if needed!)

**Score: ___/10** | **Public Accessible: ☐ Yes ☐ No**

---

## 📝 METHOD 4: MQTT BROKER

### Broker Selection:
- [ ] **Free Public Brokers Tested:**
  - ☐ test.mosquitto.org (1883/8883)
  - ☐ broker.hivemq.com (1883)
  - ☐ broker.emqx.io (1883/8883)
  - Selected: _______________

### Pi5 MQTT Setup:
- [ ] Install: `pip install paho-mqtt`
- [ ] Test script created: ☐ Yes ☐ No
- [ ] Publishing data: ☐ Yes ☐ No
- [ ] Topic structure: `datalogger/[device_id]/temp/[channel]`

### Connection Tests:
- [ ] **Publish Test**
  - Connect to broker: ☐ Success ☐ Fail
  - Publish message: ☐ Success ☐ Fail
  - QoS level tested: ☐ 0 ☐ 1 ☐ 2
  
- [ ] **Subscribe Test**
  - Receive messages: ☐ Yes ☐ No
  - Latency: _____ms
  - Message order preserved: ☐ Yes ☐ No
  
- [ ] **Persistent Session**
  - Reconnection works: ☐ Yes ☐ No
  - Offline messages queued: ☐ Yes ☐ No

### Integration Tests:
- [ ] DataLogger publishes every _____ seconds
- [ ] All 8 channels publishing: ☐ Yes ☐ No
- [ ] JSON format correct: ☐ Yes ☐ No
- [ ] Timestamp included: ☐ Yes ☐ No

**Score: ___/10** | **Real-time Data: ☐ Yes ☐ No**

---

## 📝 METHOD 5: TELEGRAM BOT

### Bot Creation:
- [ ] BotFather contacted: ☐ Yes ☐ No
- [ ] Bot username: @_______________
- [ ] Bot token received: ☐ Yes ☐ No
- [ ] Token secured: ☐ Yes ☐ No

### Pi5 Integration:
- [ ] Install: `pip install python-telegram-bot`
- [ ] Bot script created: ☐ Yes ☐ No
- [ ] Commands implemented:
  - ☐ `/status` - System status
  - ☐ `/temp [channel]` - Get temperature
  - ☐ `/start_logging` - Start logging
  - ☐ `/stop_logging` - Stop logging
  - ☐ `/alert [threshold]` - Set alerts

### Functionality Tests:
- [ ] **Message Sending**
  - Text messages: ☐ Works ☐ Fails
  - Charts/Images: ☐ Works ☐ Fails
  - Response time: _____ms
  
- [ ] **Command Processing**
  - Commands received: ☐ Yes ☐ No
  - Responses sent: ☐ Yes ☐ No
  - Error handling: ☐ Yes ☐ No
  
- [ ] **Alert System**
  - Threshold alerts: ☐ Works ☐ Fails
  - Connection loss alerts: ☐ Works ☐ Fails
  - Daily summaries: ☐ Works ☐ Fails

### Security:
- [ ] Chat ID whitelisting: ☐ Enabled ☐ Disabled
- [ ] Rate limiting: ☐ Yes ☐ No

**Score: ___/10** | **Notification Ready: ☐ Yes ☐ No**

---

## 📝 METHOD 6: CLOUD DATA BROKERS

### ThingSpeak Setup:
- [ ] Account created: ☐ Yes ☐ No
- [ ] Channel created: ☐ Yes ☐ No
- [ ] API Write Key: _______________
- [ ] Fields configured (8 temps): ☐ Yes ☐ No

### Data Publishing:
- [ ] Test data sent: ☐ Success ☐ Fail
- [ ] Update rate: Every _____ seconds
- [ ] All channels visible: ☐ Yes ☐ No
- [ ] Charts configured: ☐ Yes ☐ No

### Other Platforms Tested:
- [ ] ☐ Adafruit IO
- [ ] ☐ Blynk
- [ ] ☐ Cayenne myDevices
- [ ] ☐ Google Cloud IoT
- [ ] ☐ AWS IoT Core
- [ ] ☐ Azure IoT Hub

**Score: ___/10** | **Cloud Storage: ☐ Yes ☐ No**

---

## 📝 METHOD 7: SSH REVERSE TUNNEL

### VPS/Cloud Server (if applicable):
- [ ] Server IP: ___.___.___.___
- [ ] SSH access confirmed: ☐ Yes ☐ No
- [ ] Ports available: _______________

### Tunnel Setup:
- [ ] Command: `ssh -R 8080:localhost:8080 user@server`
- [ ] Connection established: ☐ Yes ☐ No
- [ ] Auto-reconnect script: ☐ Created ☐ No
- [ ] SystemD service: ☐ Created ☐ No

### Access Tests:
- [ ] Web access via VPS: ☐ Works ☐ Fails
- [ ] Persistent connection: ☐ Yes ☐ No
- [ ] Through firewall: ☐ Yes ☐ No

**Score: ___/10** | **Requires VPS: ☐ Yes ☐ No**

---

## 🔒 SECURITY ASSESSMENT

### Current Vulnerabilities:
- [ ] Default passwords changed: ☐ Yes ☐ No
- [ ] SSH key authentication: ☐ Enabled ☐ Disabled
- [ ] Web interface authentication: ☐ Yes ☐ No
- [ ] HTTPS enabled: ☐ Yes ☐ No
- [ ] Firewall configured: ☐ Yes ☐ No
- [ ] Fail2ban installed: ☐ Yes ☐ No

### Recommended Security Measures:
- [ ] ☐ Add basic auth to Flask app
- [ ] ☐ Use HTTPS certificates
- [ ] ☐ Implement API key authentication
- [ ] ☐ Enable UFW firewall
- [ ] ☐ Set up log monitoring
- [ ] ☐ Regular security updates

---

## 📊 FINAL COMPARISON MATRIX

| Method | Setup Easy | Firewall OK | Remote Access | Real-time | Score |
|--------|------------|-------------|---------------|-----------|-------|
| Local Network | ⭐⭐⭐⭐⭐ | ❌ | ❌ | ✅ | ___/10 |
| Tailscale | ⭐⭐⭐⭐ | ✅ | ✅ | ✅ | ___/10 |
| Cloudflare | ⭐⭐⭐⭐ | ✅ | ✅ | ✅ | ___/10 |
| MQTT | ⭐⭐⭐ | ✅ | ✅ | ✅ | ___/10 |
| Telegram | ⭐⭐⭐ | ✅ | ✅ | ⚠️ | ___/10 |
| Cloud Broker | ⭐⭐⭐ | ✅ | ✅ | ✅ | ___/10 |
| SSH Tunnel | ⭐⭐ | ✅ | ✅ | ✅ | ___/10 |

---

## 🎯 RECOMMENDED SOLUTION

Based on testing, the best solution for this network environment is:

**Primary Method:** _______________ (Score: ___/10)
**Backup Method:** _______________ (Score: ___/10)
**Alert System:** _______________ 

### Justification:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

### Implementation Priority:
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

---

## 📝 NOTES & OBSERVATIONS

### What Worked Well:
_________________________________________________________________
_________________________________________________________________

### What Failed:
_________________________________________________________________
_________________________________________________________________

### Network Restrictions Found:
_________________________________________________________________
_________________________________________________________________

### Performance Metrics:
- Best latency: _______________ with _____ms
- Most reliable: _______________
- Easiest setup: _______________
- Most secure: _______________

---

## ✅ SIGN-OFF

**Testing Completed By:** _______________  
**Date:** _______________  
**Time Taken:** _____ hours  
**Approved By:** _______________  

---

## 📎 APPENDIX: Quick Commands Reference

```bash
# Local Network
ping 192.168.1.100
curl http://192.168.1.100:8080/api/board_info

# Tailscale
sudo tailscale status
sudo tailscale ping pi5-datalogger

# Cloudflare Tunnel
./cloudflared-linux-arm64 tunnel --url http://localhost:8080

# MQTT Test
mosquitto_pub -h test.mosquitto.org -t "test/topic" -m "Hello"
mosquitto_sub -h test.mosquitto.org -t "test/topic"

# Telegram Bot
curl https://api.telegram.org/bot[TOKEN]/getMe

# SSH Reverse Tunnel
ssh -fN -R 8080:localhost:8080 user@vps.com
```

---

**Document Version:** 1.0  
**Last Updated:** January 2025  
**Next Review:** _______________