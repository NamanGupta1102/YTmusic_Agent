from ytmusicapi import YTMusic
import os
import logging

logger = logging.getLogger(__name__)

def get_authenticated_client():
    """
    Initializes and returns an authenticated YTMusic client using browser headers.
    Expects 'browser.json' to exist in the current directory.
    """
    if not os.path.exists('browser.json'):
        raise FileNotFoundError("browser.json not found. Run setup_browser_auth.py first.")

    try:
        # Simple init with headers file
        return YTMusic(auth='browser.json')
    except Exception as e:
        logger.error(f"Failed to initialize authenticated client: {e}")
        raise

def create_playlist_from_ids(title: str, video_ids: list[str], description: str = "Created by YT Music Agent") -> str:
    """
    Creates a private playlist with the given songs.
    
    Args:
        title: Title of the playlist.
        video_ids: List of videoIds to add.
        description: Description for the playlist.
        
    Returns:
        The new Playlist ID.
    """
    try:
        yt = get_authenticated_client()
        
        logger.info(f"Creating playlist '{title}' with {len(video_ids)} songs...")
        
        playlist_id = yt.create_playlist(
            title=title,
            description=description,
            privacy_status="PRIVATE",
            video_ids=video_ids
        )
        
        logger.info(f"Playlist created successfully. ID: {playlist_id}")
        return playlist_id

    except Exception as e:
        logger.error(f"Error creating playlist: {e}")
        raise
