
try:
    from google import genai
    print("Success: from google import genai")
except ImportError as e:
    print(f"Error: {e}")
    
try:
    import google.genai
    print("Success: import google.genai")
except ImportError as e:
    print(f"Error: {e}")

import sys
print(sys.path)
