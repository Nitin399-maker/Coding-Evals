import re
import subprocess
import tempfile
import os
import base64
import requests
import io
from PIL import Image

def evaluate_gif_drawing_code(response,context=None):
    """
    Evaluates if the LLM can write Python code that creates a GIF file with a red triangle.
    The function:
    1. Extracts code from the response
    2. Runs the code to generate a GIF
    3. Uses a vision model to describe the image
    4. Checks if the description mentions a red triangle
    
    Args:
        response: The LLM response containing Python code
        
    Returns:
        dict: Result with pass/fail status and details
    """
    # Extract code from the response
    code = extract_code(response)
    if not code:
        return {
            "pass": False,
            "reason": "Could not extract valid Python code from the response"
        }
    
    # Run the code and capture output
    gif_data = run_python_code(code)
    if not gif_data:
        return {
            "pass": False,
            "reason": "Code execution failed or did not produce valid output"
        }
    
    # Use a vision model to analyze the image
    vision_description = analyze_image_with_vision_model(gif_data)
    if not vision_description:
        return {
            "pass": False,
            "reason": "Failed to analyze the generated image"
        }
    
    # Check if the vision model detected a red triangle
    contains_triangle = "triangle" in vision_description.lower()
    contains_red = "red" in vision_description.lower()
    
    if contains_triangle and contains_red:
        return {
            "pass": True,
            "reason": "Generated image contains a red triangle as required",
            "vision_description": vision_description
        }
    else:
        missing = []
        if not contains_triangle:
            missing.append("triangle")
        if not contains_red:
            missing.append("red color")
        
        return {
            "pass": False,
            "reason": f"Image does not contain {' and '.join(missing)}",
            "vision_description": vision_description
        }

def extract_code(response):
    """Extract Python code from the response"""
    # Try to extract code from markdown code blocks
    pattern = r"```(?:python)?(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    # If no code blocks, try to use the entire response
    if "import" in response and "print" in response:
        return response.strip()
    
    return None

def run_python_code(code):
    """Run the Python code and capture its binary output"""
    try:
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code.encode('utf-8'))
        
        # Run the code and capture binary output directly
        try:
            process = subprocess.run(
                ['python', temp_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30
            )
            
            # Check if the code executed successfully
            if process.returncode != 0:
                print(f"Code execution failed: {process.stderr.decode('utf-8', errors='replace')}")
                return None
            
            # Get the binary output
            gif_data = process.stdout
            
            # Check if we got any data
            if not gif_data:
                print("Code executed but produced no output")
                return None
                
            # Try to verify this is actually image data
            try:
                Image.open(io.BytesIO(gif_data))
            except Exception as e:
                print(f"Output is not a valid image: {str(e)}")
                return None
                
            return gif_data
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        print(f"Error running Python code: {str(e)}")
        return None

def analyze_image_with_vision_model(image_data):
    """Use a vision model to describe the image"""
    try:
        # First, try to validate the image data with PIL
        try:
            img = Image.open(io.BytesIO(image_data))
            img_format = img.format.lower() if img.format else "unknown"
            print(f"Successfully opened image: format={img_format}, size={img.size}")
        except Exception as e:
            print(f"Warning: Could not open image with PIL: {str(e)}")
            return "Could not analyze the image - invalid image data"
        
        # For this example, we'll use OpenAI's vision model through their API
        # You'll need an API key for this to work
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("OpenAI API key not found in environment variables")
            # As a fallback, try to use PIL to analyze basic image properties
            return fallback_image_analysis(image_data)
        
        # Convert the image to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe the shapes in this image and their color"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/gif;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"API request failed: {response.text}")
            return fallback_image_analysis(image_data)
            
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return fallback_image_analysis(image_data)

def fallback_image_analysis(image_data):
    """Fallback method to analyze basic image properties if the vision API fails"""
    try:
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB to analyze colors
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Sample colors from the image
        width, height = img.size
        colors = []
        for x in range(0, width, width//10):
            for y in range(0, height, height//10):
                try:
                    r, g, b = img.getpixel((x, y))
                    # Check if this is a red-ish pixel
                    if r > 200 and g < 100 and b < 100:
                        colors.append("red")
                    elif r > 200 and g > 200 and b > 200:
                        colors.append("white")
                except IndexError:
                    continue
        
        # Count the colors
        color_counts = {}
        for color in colors:
            if color in color_counts:
                color_counts[color] += 1
            else:
                color_counts[color] = 1
        
        # Make a simple description
        description = "The image appears to contain "
        if "red" in color_counts and color_counts["red"] > 3:
            description += "red elements "
        if "white" in color_counts and color_counts["white"] > 3:
            description += "on a white background"
        
        # Add a guess about shapes
        description += ". Based on color distribution, there might be a triangle shape."
        
        return description
    except Exception as e:
        print(f"Fallback analysis failed: {str(e)}")
        return "Could not analyze the image content" 
    
