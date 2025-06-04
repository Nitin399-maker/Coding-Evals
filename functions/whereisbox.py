def check_latex_package_knowledge(response,context=None):
    """
    Checks if the LLM response correctly identifies the LaTeX package 
    that provides the Sbox environment.
    
    Args:
        response: The LLM response to the LaTeX package question
        
    Returns:
        dict: Result with pass/fail status and details
    """
    # The correct package name
    correct_package = "fancybox"
    
    # Check if the correct package name is mentioned in the response
    response_lower = response.lower()
    contains_correct_package = correct_package.lower() in response_lower
    
    # Create a detailed reason
    if contains_correct_package:
        reason = f"Response correctly mentions the '{correct_package}' package."
    else:
        reason = f"Response does not mention the '{correct_package}' package."
        
        # Try to extract what package was mentioned instead
        import re
        package_mentions = re.findall(r'\\usepackage\{([^}]+)\}', response)
        if package_mentions:
            reason += f" Instead mentioned: {', '.join(package_mentions)}"
    print(reason)
    return {
        "pass": contains_correct_package,
        "score": 1.0 if contains_correct_package else 0.0,
        "reason": reason
    }
    
