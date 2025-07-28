from flask import Flask, render_template, jsonify
from database import get_latest_readings, get_historical_data
from data_logger import start_logging_thread

app = Flask(__name__)

@app.route('/')
def index():
    """Serves the main dashboard page."""
    return render_template('index.html')

@app.route('/api/data/latest')
def api_latest_data():
    """API endpoint to get the latest reading for each thermocouple."""
    try:
        readings = get_latest_readings()
        return jsonify(readings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/historical')
def api_historical_data():
    """API endpoint to get historical data for the charts."""
    try:
        # In a real app, you might pass a time range from the client
        readings = get_historical_data(hours=24)  # Default to last 24 hours
        return jsonify(readings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start the background thread for data logging
    start_logging_thread()
    
    # Run the Flask app
    # Use debug=True for development, but turn it off for production
    app.run(host='0.0.0.0', port=5000, debug=True)