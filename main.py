import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Import our modular tools
from tools.search_tool import search_song
from tools.artist_tool import get_artist_top_songs
from tools.playlist_tool import create_playlist_from_ids
from tools.recommendation_tool import get_recommendations

# Import State
from agent.state import SessionState

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY missing. Please check your .env file.")
    exit(1)

GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")

# Global State
session = SessionState()

# --- WRAPPER TOOLS FOR AGENT ---

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
    """Gets recommendations based on a seed song. Checks for valid seed first."""
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
    """Searches for a song and adds the best match to the User's Cart."""
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


# --- MAIN AGENT LOOP ---

def main():
    print(f"Initializing Gemini Client (New SDK)...")
    print(f"Model: {GEMINI_MODEL_NAME}")
    
    client = genai.Client(api_key=GEMINI_API_KEY)

    system_instruction = """
    You are an intelligent Music Curator Agent for YouTube Music.
    
    **Your Goal**: Help the user build a perfect playlist through conversation.
    **Your Memory**: You have a "Shopping Cart" (`session`) where you store songs the user likes.
    
    **Workflow**:
    1. **Discvoery**: Use `get_artist_songs` or `get_song_recommendations` to find music.
    2. **Curation**: When the user likes a song (or says "add X"), use `add_song_to_cart`. 
       - NEVER add a song to the cart without User intent.
    3. **Review**: If the user asks "what do I have?", use `review_cart`.
    4. **Checkout**: When the user says "Build playlist", use `checkout_playlist`.
    
    **Tone**: Enthusiastic, knowledgeable, helper.
    """

    # Create chat session with tools
    # Note: In the new SDK, tools are passed in the config
    tools_list = [
        get_artist_songs, 
        get_song_recommendations,
        add_song_to_cart,
        remove_song_from_cart,
        review_cart,
        checkout_playlist
    ]

    chat = client.chats.create(
        model=GEMINI_MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=tools_list,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
        )
    )

    print("\n🎧 Ultimate YT Music Agent is Ready!")
    print(f"   (SDK: google-genai | Model: {GEMINI_MODEL_NAME})")
    print("----------------------------------------------------------")

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit']:
                print("Bye!")
                break
            
            if not user_input.strip():
                continue

            response = chat.send_message(user_input)
            
            if response.text:
                print(f"Agent: {response.text}")
            elif response.candidates and response.candidates[0].content.parts:
                # Fallback for complex responses that might not populate .text directly
                # (though the new SDK is usually good about this)
                print(f"Agent: {response.candidates[0].content.parts[0].text}")
            else:
                 print("Agent: (No text response)")

        except Exception as e:
            if "429" in str(e):
                print("⚠️ Quota Exceeded (429). Wait a moment.")
            else:
                logger.error(f"Chat Error: {e}")
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
