import json
import os

CALIBRATION_FILE = os.path.join(os.path.dirname(__file__), 'calibration.json')

def get_calibration_factors():
    """Reads calibration factors from the JSON file."""
    if not os.path.exists(CALIBRATION_FILE):
        return {}
    with open(CALIBRATION_FILE, 'r') as f:
        return json.load(f)

def set_calibration_factor(channel, factor):
    """Sets a calibration factor for a specific channel."""
    factors = get_calibration_factors()
    factors[str(channel)] = factor
    with open(CALIBRATION_FILE, 'w') as f:
        json.dump(factors, f, indent=4)

def apply_correction(channel, temperature):
    """Applies the calibration correction to a temperature reading."""
    factors = get_calibration_factors()
    factor = factors.get(str(channel), 1.0)  # Default to 1.0 if no factor is found
    return temperature * factor