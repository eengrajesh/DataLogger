# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Raspberry Pi temperature data logging application that reads data from up to 8 K-type thermocouples via a Sequent Microsystems 8-Thermocouple DAQ HAT. The system provides real-time monitoring, data storage, and web-based interaction.

## Architecture

### Core Components

1. **Flask Web Server** (`app.py`): RESTful API endpoints for controlling logging, retrieving data, and managing sensors
2. **Data Logger** (`data_logger.py`): Manages hardware communication and threading for continuous temperature monitoring
3. **Hardware Abstraction** (`sm_tc/__init__.py`): I2C communication with DAQ HAT, includes Windows mock for development
4. **Database Layer** (`database.py`): SQLite database operations for storing temperature readings
5. **Calibration System** (`calibration.py`): JSON-based calibration factors for temperature correction

### Key Design Patterns

- **Multi-threading**: Background logging thread with stop event control
- **Hardware Abstraction**: Platform-specific implementations (real hardware vs mock)
- **Per-channel Configuration**: Individual sensor intervals and active status
- **RESTful API**: All functionality exposed through HTTP endpoints

## Development Commands

### Initial Setup
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r data-logger-project/requirements.txt

# Initialize database
python data-logger-project/database.py
```

### Running the Application
```bash
# Development server (port 8080)
python data-logger-project/app.py

# Production with gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 data-logger-project.wsgi:app
```

### Testing
```bash
# Test DAQ hardware connection
python data-logger-project/test_daq.py

# Test network connectivity
python data-logger-project/ping_test.py
```

## Hardware Configuration

- **I2C Address**: Base address 0x16 + stack level (0-7)
- **I2C Bus**: Default bus 1 on Raspberry Pi
- **Thermocouple Types**: B, E, J, K (default), N, R, S, T
- **Temperature Scale**: Raw values divided by 10.0

## Database Schema

Single table `readings`:
- `id`: Primary key
- `timestamp`: DateTime (auto-generated)
- `thermocouple_id`: Channel number (1-8)
- `temperature`: Corrected temperature value

## API Endpoints

### Data Operations
- `GET /api/data/live/<channel>`: Live temperature from specific channel
- `GET /api/data/latest`: Latest reading for each thermocouple
- `GET /api/data/historical`: Historical data (default 24 hours)
- `GET /api/data/average`: Average temperature per channel
- `GET /api/data/download/<format>`: Export data (json/csv)
- `POST /api/data/clear`: Clear all database records

### Control Operations
- `POST /api/logging/start`: Start background logging thread
- `POST /api/logging/stop`: Stop background logging thread
- `POST /api/connect`: Connect to DAQ hardware
- `POST /api/disconnect`: Disconnect from DAQ hardware

### Configuration
- `POST /api/sensor_status/<channel>`: Enable/disable channel
- `POST /api/sensor_interval/<channel>`: Set sampling interval
- `GET /api/calibration`: Get calibration factors
- `POST /api/calibration/<channel>`: Set calibration factor

### System Information
- `GET /api/board_info`: DAQ board details
- `GET /api/storage_status`: Disk usage
- `GET /api/cpu_temp`: Raspberry Pi CPU temperature

## Development Notes

- Windows development uses `MockSMtc` class that simulates temperature readings
- Database file `datalogger.db` is gitignored
- Default sampling interval: 5 seconds per channel
- Calibration factors stored in `calibration.json`
- Web interface served from `templates/index.html`