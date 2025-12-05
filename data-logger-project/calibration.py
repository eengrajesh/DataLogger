import json
import os

CALIBRATION_FILE = os.path.join(os.path.dirname(__file__), 'calibration.json')

def get_calibration_factors():
    """Reads calibration data from the JSON file."""
    if not os.path.exists(CALIBRATION_FILE):
        return {}
    with open(CALIBRATION_FILE, 'r') as f:
        return json.load(f)

def save_calibration_factors(factors):
    """Saves calibration data to the JSON file."""
    with open(CALIBRATION_FILE, 'w') as f:
        json.dump(factors, f, indent=4)

def set_calibration_factor(channel, factor):
    """Sets a simple multiplier calibration factor for a specific channel."""
    factors = get_calibration_factors()
    channel_key = str(channel)

    # If channel doesn't exist, create it with default structure
    if channel_key not in factors or not isinstance(factors.get(channel_key), dict):
        factors[channel_key] = {
            "factor": factor,
            "slope": 1.0,
            "offset": 0.0,
            "ice_reading": None,
            "boil_reading": None,
            "calibration_method": "simple"
        }
    else:
        factors[channel_key]["factor"] = factor
        factors[channel_key]["calibration_method"] = "simple"

    save_calibration_factors(factors)

def set_two_point_calibration(channel, ice_reading, boil_reading, actual_ice=0.0, actual_boil=100.0):
    """
    Sets two-point linear calibration for a specific channel.

    Two-point calibration uses:
    - Ice bath reading (should be 0°C)
    - Boiling water reading (should be ~100°C, depends on altitude)

    Linear equation: corrected_temp = slope * raw_temp + offset

    Where:
        slope = (actual_boil - actual_ice) / (boil_reading - ice_reading)
        offset = actual_ice - (slope * ice_reading)

    Args:
        channel: Channel number (1-8)
        ice_reading: Raw temperature reading in ice bath
        boil_reading: Raw temperature reading in boiling water
        actual_ice: Actual ice bath temperature (default 0.0°C)
        actual_boil: Actual boiling point (default 100.0°C, adjust for altitude)

    Returns:
        dict with slope and offset values
    """
    factors = get_calibration_factors()
    channel_key = str(channel)

    # Avoid division by zero
    if boil_reading == ice_reading:
        raise ValueError("Ice and boiling readings cannot be the same")

    # Calculate slope and offset for linear calibration
    # Formula: corrected = slope * raw + offset
    slope = (actual_boil - actual_ice) / (boil_reading - ice_reading)
    offset = actual_ice - (slope * ice_reading)

    # Calculate equivalent simple factor (for backward compatibility display)
    # This is approximate - the two-point method is more accurate
    simple_factor = slope

    # Store calibration data
    factors[channel_key] = {
        "factor": round(simple_factor, 4),
        "slope": round(slope, 6),
        "offset": round(offset, 4),
        "ice_reading": ice_reading,
        "boil_reading": boil_reading,
        "actual_ice": actual_ice,
        "actual_boil": actual_boil,
        "calibration_method": "two_point"
    }

    save_calibration_factors(factors)

    return {
        "slope": factors[channel_key]["slope"],
        "offset": factors[channel_key]["offset"],
        "factor": factors[channel_key]["factor"]
    }

def get_channel_calibration(channel):
    """Gets full calibration data for a specific channel."""
    factors = get_calibration_factors()
    channel_key = str(channel)

    if channel_key not in factors:
        return {
            "factor": 1.0,
            "slope": 1.0,
            "offset": 0.0,
            "ice_reading": None,
            "boil_reading": None,
            "calibration_method": "none"
        }

    data = factors[channel_key]

    # Handle legacy format (just a number)
    if isinstance(data, (int, float)):
        return {
            "factor": data,
            "slope": data,
            "offset": 0.0,
            "ice_reading": None,
            "boil_reading": None,
            "calibration_method": "simple"
        }

    return data

def apply_correction(channel, temperature):
    """
    Applies the calibration correction to a temperature reading.

    Uses two-point linear calibration if available, otherwise falls back to simple factor.
    If calibration_method is "none", returns the raw temperature unchanged.

    Formula: corrected_temp = slope * raw_temp + offset
    """
    cal_data = get_channel_calibration(channel)

    method = cal_data.get("calibration_method", "none")

    if method == "none":
        # No calibration - return raw temperature unchanged
        return temperature
    elif method == "two_point":
        # Use linear calibration: y = mx + b
        slope = cal_data.get("slope", 1.0)
        offset = cal_data.get("offset", 0.0)
        return (temperature * slope) + offset
    else:
        # Use simple multiplication factor
        factor = cal_data.get("factor", 1.0)
        if isinstance(factor, (int, float)):
            return temperature * factor
        return temperature

def reset_channel_calibration(channel):
    """Resets calibration for a specific channel to defaults."""
    factors = get_calibration_factors()
    channel_key = str(channel)

    factors[channel_key] = {
        "factor": 1.0,
        "slope": 1.0,
        "offset": 0.0,
        "ice_reading": None,
        "boil_reading": None,
        "calibration_method": "none"
    }

    save_calibration_factors(factors)
    return factors[channel_key]
