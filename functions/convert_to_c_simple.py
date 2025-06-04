import re
import subprocess
import tempfile
import os

def evaluate_python_to_c_conversion(response,context=None):
    """
    Evaluates if the LLM correctly rewrote a Python sqrt function in C.
    Tests if the C implementation produces the correct output when run.
    
    Args:
        response: The LLM response with the C code
        
    Returns:
        dict: Result with pass/fail status and details
    """
    # Extract C code from the response
    c_code = extract_code(response)
    if not c_code:
        return {
            "pass": False,
            "score": 0.0,
            "reason": "Could not extract valid C code from the response"
        }
     
    c_code = re.sub(
    r'\s*int\s+main\s*\([^)]*\)\s*\{[^{}]*\{[^{}]*\}[^{}]*\}|\s*int\s+main\s*\([^)]*\)\s*\{.*?\}\s*',
    '', 
    c_code, 
    flags=re.DOTALL)
   
    # Create the test case code
    test_case = """
    #include <stdio.h>
    
    int main() {
        printf("%d\\n", (int)(my_sqrt(12345, .001)*10));
        return 0;
    }
    """
    
    # Run the code with the test case
    compile_output, run_output = compile_and_run_c(c_code, test_case)
    print(compile_output, run_output)
    # Check if compilation failed
    if "error" in compile_output.lower():
        return {
            "pass": False,
            "score": 0.0,
            "reason": f"C code compilation failed: {compile_output}",
            "code": c_code
        }
    
    # Check if the output is correct (should contain "1111")
    expected_output = "1111"
    contains_expected = expected_output in run_output
    if contains_expected:
        reason = f"C code correctly implements the square root function, producing output: {run_output.strip()}"
    else:
        reason = f"C code did not produce the expected output '{expected_output}'. Got: '{run_output.strip()}'"
    print(reason)
    
    return {
        "pass": contains_expected,
        "score": 1.0 if contains_expected else 0.0,
        "reason": reason
    }

def extract_code(response):
    """Extract C code from the LLM response"""
    # Try to extract code from markdown code blocks
    pattern = r"```(?:c|cpp)?(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)
    
    if matches:
        # Return the content of the first code block
        return matches[0].strip()
    
    # If no code blocks, try to detect C code patterns
    if "#include" in response and "float my_sqrt" in response:
        # Assuming the entire response is code or we need to extract the function
        c_code_pattern = r"(#include.*?float\s+my_sqrt.*?\})"
        c_match = re.search(c_code_pattern, response, re.DOTALL)
        if c_match:
            return c_match.group(1)
        
        # If we can't match the whole thing, just return the function
        func_pattern = r"(float\s+my_sqrt.*?\})"
        func_match = re.search(func_pattern, response, re.DOTALL)
        if func_match:
            return "#include <stdio.h>\n#include <math.h>\n\n" + func_match.group(1)
    
    return None

def compile_and_run_c(code, test_case):
    """Compile and run C code with the given test case"""
    try:
        # Create a temporary directory to work in
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create the source file with both the function and test case
            source_path = os.path.join(temp_dir, 'program.c')
            with open(source_path, 'w') as f:
                f.write(code + "\n\n" + test_case)
            
            # Compile the C code
            compile_process = subprocess.run(
                ['gcc', '-o', os.path.join(temp_dir, 'a.out'), source_path, '-lm'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            compile_output = compile_process.stdout + compile_process.stderr
            
            # If compilation failed, return the error
            if compile_process.returncode != 0:
                return compile_output, ""
            
            # Run the compiled program
            run_process = subprocess.run(
                [os.path.join(temp_dir, 'a.out')],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            run_output = run_process.stdout + run_process.stderr
            return compile_output, run_output
                
    except Exception as e:
        return f"Error: {str(e)}", ""
    
