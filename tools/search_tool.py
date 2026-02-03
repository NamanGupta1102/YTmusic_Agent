from ytmusicapi import YTMusic
import logging

# Configure logging (module level)
logger = logging.getLogger(__name__)

def search_song(query: str, limit: int = 5) -> list[dict]:
    """
    Search for songs on YouTube Music using the Guest Client.
    
    Args:
        query: The search string (e.g., "Bohemian Rhapsody Queen").
        limit: Number of results to return (default 5).
        
    Returns:
        A list of dictionaries containing keys: videoId, title, artist, album, duration.
        Returns an empty list if no results found or on error.
    """
    try:
        # Initialize Guest Client (Unauthenticated - bypasses 400 Bad Request on Search)
        yt_guest = YTMusic()
        
        # Perform search
        logger.info(f"Searching for '{query}'...")
        raw_results = yt_guest.search(query=query, filter="songs", limit=limit)
        
        parsed_results = []
        for res in raw_results:
            try:
                # Safe extraction with defaults
                video_id = res.get('videoId')
                if not video_id:
                    continue # Skip if no videoId

                title = res.get('title', 'Unknown Title')
                
                # Artists is a list of dicts: [{'name': 'Artist', 'id': '...'}]
                artists_list = res.get('artists', [])
                artist = artists_list[0]['name'] if artists_list else "Unknown Artist"
                
                # Album is a dict: {'name': 'Album', 'id': '...'}
                album_info = res.get('album')
                album = album_info['name'] if album_info else "Unknown Album"
                
                duration = res.get('duration', '0:00')
                
                parsed_results.append({
                    "videoId": video_id,
                    "title": title,
                    "artist": artist,
                    "album": album,
                    "duration": duration
                })
                
            except Exception as e:
                logger.warning(f"Error parsing a search result: {e}")
                continue

        logger.info(f"Found {len(parsed_results)} results for '{query}'")
        return parsed_results

    except Exception as e:
        logger.error(f"Search failed for query '{query}': {e}")
        return []
