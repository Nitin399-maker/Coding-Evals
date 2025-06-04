def evaluate_numpy_understanding(response,context=None):
    """
    Evaluates if the LLM correctly understands numpy advanced indexing.
    Checks if the response includes the correct output shape: (3, 20)
    
    Args:
        response: The LLM's response to the numpy question
        
    Returns:
        dict: Result with pass/fail status and details
    """
    # The expected output from the numpy code
    expected_output = "The array shape is (3, 20)"
    
    # Check if the response contains the expected output
    contains_expected = expected_output in response
    
    # Also check if it contains the correct shape in a different format
    alternative_formats = ["shape is (3, 20)", "shape: (3, 20)", "array.shape = (3, 20)"]
    contains_alternative = any(alt in response for alt in alternative_formats)
    
    # The test passes if either the exact expected output or an alternative format is present
    overall_success = contains_expected or contains_alternative
    
    # Extract the shape the model predicted (for diagnostics)
    import re
    shape_match = re.search(r"shape(?:\s+is|\s*[:=]\s*)\s*\((\d+),\s*(\d+)\)", response)
    predicted_shape = f"({shape_match.group(1)}, {shape_match.group(2)})" if shape_match else "not found"
    
    # Build the reason message
    if overall_success:
        reason = f"Response correctly explains that the shape is (3, 20)"
    else:
        reason = f"Response does not correctly identify the shape as (3, 20). Predicted shape: {predicted_shape}"
        
    print(expected_output, predicted_shape, overall_success)
    return {
        "pass": overall_success,
        "score": 1.0 if overall_success else 0.0,
        "reason": reason,
        "expected_output": expected_output,
        "predicted_shape": predicted_shape
    }
    
