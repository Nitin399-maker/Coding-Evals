import re
import subprocess
import tempfile
import os

def evaluate_traceback_fix(response,context=None):
    """
    Evaluates if the LLM correctly fixed the Python program that handles tracebacks.
    Tests if the fixed code outputs both "x: 5" and "y: 6" when run.
    
    Args:
        response: The LLM response with the fixed code
        
    Returns:
        dict: Result with pass/fail status and details
    """
    # Extract code from the response
    code = extract_code(response)
    if not code:
        return {
            "pass": False,
            "score": 0.0,
            "reason": "Could not extract valid Python code from the response"
        }
    
    # Run the extracted code
    program_output = run_python_code(code)
    
    # Check if required output strings are present
    contains_x5 = "x: 5" in program_output
    contains_y6 = "y: 6" in program_output
    
    # Determine overall success
    overall_success = contains_x5 and contains_y6
    print(program_output, contains_x5, contains_y6)
    # Build reason message
    reason_parts = []
    if contains_x5:
        reason_parts.append("Code correctly outputs 'x: 5'")
    else:
        reason_parts.append("Code does not output 'x: 5' and got this by running the python code " + program_output)
    
    if contains_y6:
        reason_parts.append("Code correctly outputs 'y: 6'")
    else:
        reason_parts.append("Code does not output 'y: 6' and got this by running the python code " + program_output)
    
    return {
        "pass": overall_success,
        "score": 1.0 if overall_success else 0.0,
        "reason": " and ".join(reason_parts),
        "program_output": program_output,
        "contains_x5": contains_x5,
        "contains_y6": contains_y6
    }

def extract_code(response):
    """Extract Python code from the LLM response"""
    # Try to extract code from markdown code blocks
    pattern = r"```(?:python)?(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)
    
    if matches:
        # Return the content of the first code block
        return matches[0].strip()
    
    # If no code blocks, try to detect Python code
    if "import traceback" in response and "def" in response:
        # Assuming the entire response is code
        return response.strip()
    
    return None

def run_python_code(code):
    """Run the Python code and return the output"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code.encode('utf-8'))
        
        # Run the Python code
        try:
            process = subprocess.run(
                ['python', temp_file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Combine stdout and stderr for comprehensive output
            output = process.stdout
            if process.stderr:
                output += "\nERROR: " + process.stderr
                
            return output.strip()
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        return f"Error running Python code: {str(e)}"
    
    
