# Requirements Gap Analysis - Thermocouple Data Logger

## Project Overview
Raspberry Pi 5-Based Thermocouple Data Logger with SMTC Interface - A system designed to monitor and record temperature data from up to eight thermocouples with support for both local data storage and database logging.

## Current Requirements vs Implementation Status

### ✅ Implemented Features
- Web-based Flask interface
- Basic SMTC board connection/disconnection
- 8-channel thermocouple support
- Individual channel enable/disable
- Per-channel sampling rate configuration
- Live temperature display
- Historical data viewing
- SQLite database storage
- Basic CSV/JSON export

### ❌ Missing Features & Gaps

#### 1. **PostgreSQL Database Support**
- **Required**: Option to connect to PostgreSQL (local or remote)
- **Current**: Only SQLite implementation
- **Gap**: No PostgreSQL drivers, connection configuration, or UI options

#### 2. **Local Storage Options**
- **Required**: SD card and USB storage support
- **Current**: Fixed SQLite location in project directory
- **Gap**: No storage device detection, selection, or management

#### 3. **Connection Status Tile**
- **Required**: Real-time status display showing:
  - Board connectivity status
  - Local storage status and availability
  - Database connection status (enabled/disabled, storage size)
- **Current**: Basic connection status only
- **Gap**: Missing comprehensive status dashboard

#### 4. **Desktop Launch Integration**
- **Required**: Single command launch via bash script or desktop icon
- **Current**: Manual Python script execution
- **Gap**: No desktop integration or auto-start configuration

#### 5. **Enhanced Visualization Tools**
- **Required**: 
  - Interactive graph controls (zoom, pan)
  - Adjustable time range (x-axis) and temperature range (y-axis)
  - Data extraction based on date/time range
- **Current**: Basic static graphs
- **Gap**: Limited interactivity and range selection

#### 6. **Data Management Features**
- **Required**: CSV export with custom date/time range selection
- **Current**: Full data export only
- **Gap**: No selective export or data filtering options

#### 7. **Raspberry Pi 5 Optimization**
- **Required**: Pi 5 specific configuration
- **Current**: Generic Raspberry Pi support
- **Gap**: No Pi 5 specific optimizations

## Priority Implementation Roadmap

### Phase 1: Core Database & Storage
1. Implement PostgreSQL support with connection pooling
2. Add storage device detection (SD/USB)
3. Create database selection UI (SQLite/PostgreSQL/local/remote)

### Phase 2: UI Enhancement
1. Develop comprehensive status dashboard tile
2. Add interactive graph controls (plotly.js or similar)
3. Implement date/time range selectors for data export

### Phase 3: System Integration
1. Create bash launch script
2. Add desktop shortcut (.desktop file)
3. Configure systemd service for auto-start

### Phase 4: Data Management
1. Implement selective CSV export with filters
2. Add data retention policies
3. Create backup/restore functionality

### Phase 5: Optimization
1. Raspberry Pi 5 specific configurations
2. Performance tuning for real-time data
3. Memory optimization for long-term logging

## Technical Requirements

### Software Dependencies Needed
- psycopg2 (PostgreSQL adapter)
- pyudev (USB device detection)
- plotly (interactive graphs)
- pandas (advanced data manipulation)

### Hardware Considerations
- Raspberry Pi 5 with latest Raspberry Pi OS
- SMTC 8-thermocouple DAQ HAT
- SD card or USB storage device
- Network connectivity for remote database

## Notes
- Consider implementing data buffering for network interruptions
- Add configuration file for system settings
- Implement proper error handling for hardware disconnections
- Consider adding email/SMS alerts for critical temperatures