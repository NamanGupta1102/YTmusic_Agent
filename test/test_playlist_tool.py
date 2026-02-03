import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.playlist_tool import create_playlist_from_ids
from tools.search_tool import search_song

def main():
    print("Testing tools/playlist_tool.py...")
    
    # 1. Find a song ID to use
    print("Finding a song to add...")
    songs = search_song("Never Gonna Give You Up", limit=1)
    if not songs:
        print("❌ Could not find a song to test with.")
        return
        
    video_id = songs[0]['videoId']
    title = songs[0]['title']
    print(f"Using song: {title} ({video_id})")

    # 2. Create Playlist
    playlist_title = f"Agent Test {int(time.time())}"
    print(f"Creating playlist '{playlist_title}'...")
    
    try:
        playlist_id = create_playlist_from_ids(
            title=playlist_title,
            video_ids=[video_id],
            description="Automated test from agent tools"
        )
        
        print(f"\n✅ Success! Playlist Created.")
        print(f"Playlist ID: {playlist_id}")
        print(f"Check it here: https://music.youtube.com/library/playlists")
        
    except Exception as e:
        print(f"\n❌ Failed to create playlist: {e}")

if __name__ == "__main__":
    main()
