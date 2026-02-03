import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_gemini():
    # Load .env from project root (one level up)
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env")
        return

    print(f"API Key found: {api_key[:10]}...")
    
    try:
        model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-pro") # Fallback
        print(f"Using Model: {model_name}")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        print("Sending request to Gemini...")
        response = model.generate_content("Say 'Hello, I am ready!' if you can hear me.")
        
        print(f"\n🤖 Gemini Reply: {response.text}")
        print("✅ Gemini API is working correctly.")
        
    except Exception as e:
        print(f"\n❌ API Error: {e}")

if __name__ == "__main__":
    test_gemini()
