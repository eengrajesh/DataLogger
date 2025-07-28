# Raspberry Pi Temperature Data Logger

This project provides a complete web-based temperature data logging solution for a Raspberry Pi equipped with the "Eight Thermocouples DAQ 8-Layer Stackable HAT" from Sequent Microsystems. It continuously reads data from up to eight K-type thermocouples, stores it in a local database, and presents it through a clean, real-time web interface.

## Features

- **Real-time Monitoring:** View the latest temperature from all eight thermocouples on a single dashboard.
- **Historical Data Visualization:** An interactive chart displays temperature trends over the last 24 hours.
- **Web-Based UI:** Access the dashboard from any device on your local network.
- **Scalable Architecture:** The code is structured to be easily maintainable and extensible.
- **Automated Logging:** A background service ensures that data is always being recorded.
- **Headless Operation:** The application is designed to run as a system service, starting automatically on boot.

## Technology Stack

- **Backend:** Python, Flask, Gunicorn
- **Frontend:** HTML, CSS, JavaScript (with Chart.js)
- **Database:** SQLite
- **Hardware:** Raspberry Pi 5, Sequent Microsystems 8-Thermocouple DAQ HAT

---

## Installation and Setup Guide

Follow these steps to get the data logger running on your Raspberry Pi.

### Step 1: Hardware Setup

1.  **Assemble Hardware:** Securely stack the "Eight Thermocouples DAQ HAT" onto the Raspberry Pi 5's GPIO pins.
2.  **Connect Thermocouples:** Connect your K-type thermocouples to the screw terminals on the DAQ HAT.
3.  **Power Up:** Connect the power supply to the Raspberry Pi.

### Step 2: Raspberry Pi Configuration

1.  **Install Raspberry Pi OS:** Ensure you have the latest version of Raspberry Pi OS installed on your microSD card.
2.  **Enable I2C Interface:**
    - Open a terminal and run `sudo raspi-config`.
    - Navigate to `Interface Options` -> `I2C` and select `<Yes>` to enable it.
3.  **Update System:**
    ```bash
    sudo apt update
    sudo apt upgrade -y
    ```
4.  **Install System Dependencies:**
    ```bash
    sudo apt install python3 python3-pip python3-venv -y
    ```

### Step 3: Application Setup

1.  **Clone or Copy Project:**
    - Transfer the `data-logger-project` folder to your Raspberry Pi's home directory (e.g., `/home/pi/`).
2.  **Set up Python Virtual Environment:**
    ```bash
    cd /home/pi/data-logger-project
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Install DAQ HAT Library:**
    - Follow the manufacturer's instructions to install the necessary software for the DAQ HAT. This is a critical step to enable communication with the hardware.
5.  **Initialize the Database:**
    - Run the database script once to create the `datalogger.db` file.
    ```bash
    python database.py
    ```

### Step 4: Running the Application

You can run the application in two modes:

**A) Development Mode (for testing):**

This is useful for seeing logs directly in your terminal.

```bash
# Make sure your virtual environment is active
# (source venv/bin/activate)
python app.py
```

The application will be accessible at `http://<your_pi_ip_address>:5000`.

**B) Production Mode (for deployment):**

This will run the application as a background service that starts automatically on boot.

1.  **Create the `systemd` Service File:**
    ```bash
    sudo nano /etc/systemd/system/datalogger.service
    ```
2.  **Paste the following content into the file.** **IMPORTANT:** Replace `<user>` with your actual username (e.g., `pi`).

    ```ini
    [Unit]
    Description=Data Logger Application
    After=network.target

    [Service]
    User=<user>
    Group=www-data
    WorkingDirectory=/home/<user>/data-logger-project
    ExecStart=/home/<user>/data-logger-project/venv/bin/gunicorn --workers 3 --bind unix:datalogger.sock -m 007 wsgi:app
    ExecStartPre=/home/<user>/data-logger-project/venv/bin/python /home/<user>/data-logger-project/data_logger.py &
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

3.  **Enable and Start the Service:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl start datalogger.service
    sudo systemctl enable datalogger.service
    ```
4.  **Check the Status:**
    ```bash
    sudo systemctl status datalogger.service
    ```

### Step 5: Access the Web Interface

1.  Find your Raspberry Pi's IP address by running `hostname -I`.
2.  Open a web browser on any computer on the same network and navigate to `http://<your_pi_ip_address>`.
