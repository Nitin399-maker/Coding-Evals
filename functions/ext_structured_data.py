def check_train_schedule(response,context=None):
    """
    Checks if the response contains the expected time and station information.
    
    Args:
        response: The LLM response containing train schedule information
        
    Returns:
        dict: Result with pass/fail status and details
    """
    # Expected substrings
    expected_time = "6:41"
    expected_station = "Millbrae"
    
    # Convert response to lowercase for case-insensitive matching
    response_lower = response.lower()
    
    # Check if both required strings are present
    has_time = expected_time in response
    has_station = expected_station.lower() in response_lower
    
    # Prepare detailed results
    print({
        "reason": {
            "found_time": has_time,
            "found_station": has_station,
            "expected_time": expected_time,
            "expected_station": expected_station
        }
    })
    result = {
        "pass": has_time and has_station,
        "score": 1.0 if (has_time and has_station) else 0.0,
        "reason": {
            "found_time": has_time,
            "found_station": has_station,
            "expected_time": expected_time,
            "expected_station": expected_station
        }
    }
    
    # Add reason for failure if applicable
    if not result["pass"]:
        missing = []
        if not has_time:
            missing.append(f"expected time {expected_time}")
        if not has_station:
            missing.append(f"expected station {expected_station}")
        result["reason"] = f"Missing {' and '.join(missing)}"
    else:
        result["reason"] = "Found both expected time and station"
    
    return result


check_train_schedule("""
Based on the train timetable provided, here's how you can get from Belmont station to San Bruno as soon as possible:

Since it's currently 6:41pm and you're at Belmont station, your best option is:

1. Take northbound Train #415 (Local L4 service)
   - Board at Belmont at 6:14pm
   - Arrive at San Bruno at 6:29pm

Your total journey time will be approximately 15 minutes, arriving at San Bruno at 6:29pm.

This is the earliest arrival option available from your current location and time.""")