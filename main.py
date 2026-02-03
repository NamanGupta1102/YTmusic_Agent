import os
import logging
import json
from dotenv import load_dotenv

# --- CONFIGURATION & IMPORTS ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LLM_PROVIDER = os.getenv("LLM_name", "GEMINI").upper() # GEMINI or OPENAI

# Import our modular tools
from tools.search_tool import search_song
from tools.artist_tool import get_artist_top_songs
from tools.playlist_tool import create_playlist_from_ids
from tools.recommendation_tool import get_recommendations
# Import State
from agent.state import SessionState

# Global State
session = SessionState()

# --- TOOL WRAPPERS ---
def get_artist_songs(artist_name: str) -> str:
    """Gets the top songs for a specific artist."""
    print(f"\n🤖 Agent: Getting top songs for {artist_name}...")
    songs = get_artist_top_songs(artist_name, limit=5)
    if not songs: return f"Could not find top songs for {artist_name}."
    output = f"Top songs by {artist_name} (NOT in cart yet):\n"
    for s in songs:
        output += f"- {s['title']} (Album: {s['album']})\n"
    return output + "\nAsk to add any of these to your cart!"

def get_song_recommendations(seed_song: str) -> str:
    """Gets recommendations based on a seed song."""
    print(f"\n🤖 Agent: Finding recommendations similar to '{seed_song}'...")
    found = search_song(seed_song, limit=1)
    if not found: return f"Could not find seed song '{seed_song}'."
    seed = found[0]
    recs = get_recommendations(seed['videoId'], limit=5)
    output = f"Recommendations based on '{seed['title']}' (NOT in cart yet):\n"
    for r in recs:
        output += f"- {r['title']} by {r['artist']}\n"
    return output + "\nAsk to add any of these to your cart!"

def add_song_to_cart(song_query: str) -> str:
    """Searches for a song and adds it to the Cart."""
    print(f"\n🤖 Agent: Adding '{song_query}' to cart...")
    results = search_song(song_query, limit=1)
    if not results: return f"Could not find song '{song_query}'."
    song = results[0]
    msg = session.add_song(song)
    print(f"   ✅ {msg}")
    return msg

def remove_song_from_cart(song_name_or_id: str) -> str:
    """Removes a song from the cart."""
    return session.remove_song(song_name_or_id)

def review_cart() -> str:
    """Returns the current list of songs in the cart."""
    return session.get_cart_display()

def checkout_playlist(playlist_name: str) -> str:
    """Finalizes the cart into a real YouTube Music Playlist."""
    cart = session.get_cart()
    if not cart: return "Cart is empty! add some songs first."
    print(f"\n🤖 Agent: Building playlist '{playlist_name}' with {len(cart)} songs...")
    ids = [s['videoId'] for s in cart]
    try:
        pid = create_playlist_from_ids(playlist_name, ids, "Created by AI Agent")
        session.clear()
        return f"Success! Playlist '{playlist_name}' created. ID: {pid}. Cart cleared."
    except Exception as e:
        return f"Error creating playlist: {e}"

# Map of function objects for execution handling
AVAILABLE_TOOLS = {
    "get_artist_songs": get_artist_songs,
    "get_song_recommendations": get_song_recommendations,
    "add_song_to_cart": add_song_to_cart,
    "remove_song_from_cart": remove_song_from_cart,
    "review_cart": review_cart,
    "checkout_playlist": checkout_playlist
}

SYSTEM_INSTRUCTION = """
You are an intelligent Music Curator Agent for YouTube Music.
**Your Goal**: Help the user build a perfect playlist through conversation.
**Your Memory**: You have a "Shopping Cart" where you store songs the user likes.
**Workflow**:
1. **Discovery**: Use `get_artist_songs` or `get_song_recommendations`.
2. **Curation**: When the user likes a song, use `add_song_to_cart`. (NEVER add without user intent).
3. **Review**: Use `review_cart`.
4. **Checkout**: When the user says "Build playlist", use `checkout_playlist`.
**Tone**: Enthusiastic, knowledgeable, helper.
"""

# --- GEMINI AGENT ---
def run_gemini_agent():
    from google import genai
    from google.genai import types
    
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")
    print(f"Initializing GEMINI Agent ({model_name})...")
    
    client = genai.Client(api_key=api_key)
    
    tools_list = list(AVAILABLE_TOOLS.values())
    
    chat = client.chats.create(
        model=model_name,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=tools_list,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
        )
    )
    
    print("\n🎧 Ultimate YT Music Agent (GEMINI MODE) is Ready!")
    print("----------------------------------------------------------")
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit']: break
            if not user_input.strip(): continue

            response = chat.send_message(user_input)
            if response.text:
                print(f"Agent: {response.text}")
            elif response.candidates and response.candidates[0].content.parts:
                print(f"Agent: {response.candidates[0].content.parts[0].text}")
            else:
                print("Agent: (No text response)")
                
        except Exception as e:
            if "429" in str(e): print("⚠️ Quota Exceeded (429).")
            else: print(f"Error: {e}")

# --- OPENAI AGENT ---
def run_openai_agent():
    from openai import OpenAI
    
    api_key = os.getenv("OPENAI_KEY")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
    print(f"Initializing OPENAI Agent ({model_name})...")
    
    client = OpenAI(api_key=api_key)
    
    # Define Tools Schema (OpenAI requires JSON)
    tools_schema = [
        {
            "type": "function",
            "function": {
                "name": "get_artist_songs",
                "description": "Gets top songs for a specific artist",
                "parameters": {
                    "type": "object",
                    "properties": {"artist_name": {"type": "string"}},
                    "required": ["artist_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_song_recommendations",
                "description": "Gets recommmendations based on a seed song",
                "parameters": {
                    "type": "object",
                    "properties": {"seed_song": {"type": "string"}},
                    "required": ["seed_song"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_song_to_cart",
                "description": "Searches for a song and adds it to the user's cart",
                "parameters": {
                    "type": "object",
                    "properties": {"song_query": {"type": "string"}},
                    "required": ["song_query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_song_from_cart",
                "description": "Removes a song from the cart",
                "parameters": {
                    "type": "object",
                    "properties": {"song_name_or_id": {"type": "string"}},
                    "required": ["song_name_or_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "review_cart",
                "description": "Returns the current list of songs in the cart",
                "parameters": {"type": "object", "properties": {}}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "checkout_playlist",
                "description": "Finalizes the cart into a real YouTube Music Playlist",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "playlist_name": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["playlist_name"]
                }
            }
        }
    ]
    
    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    
    print("\n🎧 Ultimate YT Music Agent (OPENAI MODE) is Ready!")
    print("----------------------------------------------------------")
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit']: break
            if not user_input.strip(): continue

            messages.append({"role": "user", "content": user_input})
            
            # loop to handle tool calls
            while True:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    tools=tools_schema
                )
                msg = response.choices[0].message
                
                if msg.tool_calls:
                    # Append assistant message with tool calls
                    messages.append(msg)
                    
                    for tool_call in msg.tool_calls:
                        fname = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)
                        func = AVAILABLE_TOOLS.get(fname)
                        
                        if func:
                            # Execute tool
                            try:
                                result = func(**args)
                            except Exception as e:
                                result = f"Error: {e}"
                                
                            # Append tool output
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": str(result)
                            })
                    # Loop back to get final response
                else:
                    # Final text response
                    print(f"Agent: {msg.content}")
                    messages.append(msg)
                    break

        except Exception as e:
            print(f"Error: {e}")


def main():
    # 1. Refresh Browser Auth from curl.txt
    try:
        from scripts.setup_browser_auth import parse_curl_and_save
        print("🔄 Refreshing Browser Auth...")
        parse_curl_and_save()
    except Exception as e:
        print(f"⚠️ Warning: Could not auto-refresh auth: {e}")

    if LLM_PROVIDER == "OPENAI":
        run_openai_agent()
    else:
        run_gemini_agent()

if __name__ == "__main__":
    main()
