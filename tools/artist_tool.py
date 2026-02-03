from ytmusicapi import YTMusic
import logging

# Configure logging
logger = logging.getLogger(__name__)

def get_artist_top_songs(artist_name: str, limit: int = 5) -> list[dict]:
    """
    Finds keywords for an artist and returns their top songs.
    
    Args:
        artist_name: Name of the artist (e.g., "The Weeknd").
        limit: Number of songs to return (default 5).
        
    Returns:
        List of dictionaries with song metadata.
    """
    try:
        # Use Guest Client
        yt = YTMusic()
        
        # 1. Search for the artist to get Browse ID
        logger.info(f"Searching for artist '{artist_name}'...")
        search_results = yt.search(query=artist_name, filter="artists")
        
        if not search_results:
            logger.warning(f"Artist '{artist_name}' not found.")
            return []
            
        # Assume top result is the correct artist
        artist_data = search_results[0]
        artist_id = artist_data.get('browseId')
        
        if not artist_id:
            logger.warning(f"No browseId found for artist '{artist_name}'")
            return []
            
        logger.info(f"Found artist '{artist_data.get('artist')}' (ID: {artist_id})")
        
        # 2. Get Artist Page
        artist_page = yt.get_artist(artist_id)
        
        # 3. Find "Songs" section
        # The structure of artist_page varies, but usually has 'songs' key if using simple access,
        # or we might need to parse sections. ytmusicapi often puts 'songs' in the 'songs' key 
        # specifically if available on the main page.
        
        # Check for 'songs' key first (simplest)
        songs_section = artist_page.get('songs')
        
        if not songs_section:
            # Sometimes it's inside 'sections'
            logger.info("Direct 'songs' key not found, searching text sections...")
            if 'sections' in artist_page:
                for section in artist_page['sections']:
                    if section.get('title') == 'Songs' or section.get('title') == 'Top songs':
                        songs_section = section # detailed list usually
                        break
        
        # If 'songs_section' is a dict with 'results', use that. 
        # If it's a list (browseId approach often returns dict with keys), let's handle `songs` key directly.
        # ytmusicapi `get_artist` returns a dict. Key `songs` usually contains a structure with `results`.
        
        results_list = []
        if songs_section and 'results' in songs_section:
            results_list = songs_section['results']
        elif isinstance(songs_section, list): 
            # unlikely for get_artist top level, but possible in some versions
            results_list = songs_section 

        if not results_list:
            logger.warning(f"No songs found on artist page for '{artist_name}'")
            return []

        # 4. Parse Keywords
        parsed_songs = []
        for song in results_list[:limit]:
            try:
                title = song.get('title')
                video_id = song.get('videoId')
                
                if not video_id: 
                    continue
                
                # Artist name is often not explicitly in the song-row if we are ON the artist page,
                # but we know the artist.
                
                parsed_songs.append({
                    "videoId": video_id,
                    "title": title,
                    "artist": artist_data.get('artist'), # Use name from search result
                    "album": song.get('album', {}).get('name', 'Unknown Album'),
                    "duration": song.get('duration', '')
                })
            except Exception as e:
                logger.warning(f"Error parsing song: {e}")
                continue
                
        return parsed_songs

    except Exception as e:
        logger.error(f"Error fetching top songs for '{artist_name}': {e}")
        return []
