# Raspberry Pi Temperature Data Logger

This project provides a web-based temperature data logging solution for a Raspberry Pi equipped with the "Eight Thermocouples DAQ 8-Layer Stackable HAT" from Sequent Microsystems. It allows users to read data from up to eight K-type thermocouples, store it in a local database, and interact with it through a real-time web interface.

## Features

-   **Real-time Monitoring:** View live temperature readings from all active channels.
-   **Historical Data Visualization:** An interactive chart displays temperature trends.
-   **UI Control:** Start and stop data logging directly from the web interface.
-   **Data Management:** Download all recorded data in CSV or JSON format and clear the database.
-   **Sensor Configuration:** Enable or disable individual sensor channels.
-   **System Status:** View DAQ HAT board information and Raspberry Pi disk space.
-   **RESTful API:** A comprehensive API for programmatic control and data retrieval.

## Technology Stack

-   **Backend:** Python, Flask
-   **Frontend:** HTML, CSS, JavaScript (with Chart.js)
-   **Database:** SQLite
-   **Hardware:** Raspberry Pi, Sequent Microsystems 8-Thermocouple DAQ HAT

---

## Quick Start Guide

Follow these steps to get the data logger running on your Raspberry Pi.

### Step 1: Prerequisites

1.  **Hardware Setup:**
    -   Stack the "Eight Thermocouples DAQ HAT" onto the Raspberry Pi's GPIO pins.
    -   Connect your K-type thermocouples to the screw terminals.
2.  **Enable I2C Interface:**
    -   Run `sudo raspi-config`.
    -   Navigate to `Interface Options` -> `I2C` and enable it.
3.  **Update System:**
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```
4.  **Install System Dependencies:**
    ```bash
    sudo apt install python3 python3-pip python3-venv -y
    ```

### Step 2: Application Setup

1.  **Clone or Copy Project:**
    -   Transfer the `data-logger-project` folder to your Raspberry Pi (e.g., `/home/pi/`).
2.  **Set up Python Virtual Environment:**
    ```bash
    cd /path/to/data-logger-project
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Initialize the Database:**
    -   Run the database script once to create the `datalogger.db` file.
    ```bash
    python database.py
    ```

### Step 3: Running the Application

1.  **Start the Flask Server:**
    -   Ensure your virtual environment is active (`source .venv/bin/activate`).
    ```bash
    python app.py
    ```
2.  **Access the Web Interface:**
    -   Find your Raspberry Pi's IP address by running `hostname -I`.
    -   Open a web browser on the same network and navigate to `http://<your_pi_ip_address>:8080`.

---

## API Documentation

The application provides a RESTful API for programmatic access. Key endpoints include:

-   `GET /api/data/live/<channel>`: Get a live reading from a specific channel.
-   `GET /api/data/historical`: Get historical data from the last 24 hours.
-   `POST /api/logging/start`: Start the data logging thread.
-   `POST /api/logging/stop`: Stop the data logging thread.
-   `GET /api/board_info`: Get information about the DAQ HAT.
-   `GET /api/storage_status`: Get the disk usage of the Raspberry Pi.
