import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.artist_tool import get_artist_top_songs

def main():
    print("Testing tools/artist_tool.py...")
    
    artist = "The Weeknd"
    print(f"Fetching top songs for: '{artist}'")
    
    songs = get_artist_top_songs(artist, limit=5)
    
    if not songs:
        print("❌ No songs found. Test Failed.")
        return

    print(f"✅ Success. Found {len(songs)} songs.")
    
    print("\nTop Song:")
    first = songs[0]
    print(f"  Title: {first.get('title')}")
    print(f"  Artist: {first.get('artist')}")
    print(f"  Album: {first.get('album')}")
    print(f"  Duration: {first.get('duration')}")
    print(f"  Video ID: {first.get('videoId')}")
    
    # Check if we actually got The Weeknd
    if "Weeknd" not in first.get('artist', ''):
         print("⚠️ Warning: Artist name might not match query exactly (could be correct if specialized).")
    
    required_keys = ["videoId", "title", "artist"]
    missing = [k for k in required_keys if k not in first]
    
    if missing:
         print(f"❌ Missing keys: {missing}")
    else:
         print("\n✅ Data structure valid.")

if __name__ == "__main__":
    main()
