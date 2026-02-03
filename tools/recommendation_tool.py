from ytmusicapi import YTMusic
import logging

logger = logging.getLogger(__name__)

def get_recommendations(video_id: str, limit: int = 20) -> list[dict]:
    """
    Get song recommendations based on a seed video ID (YouTube Music 'Radio' logic).
    
    Args:
        video_id: The videoId of the seed song.
        limit: Approximate number of songs to return.
        
    Returns:
        List of song dictionaries (videoId, title, artist, album, duration).
    """
    try:
        # Recommendations work fine with Guest Client
        yt = YTMusic()
        
        logger.info(f"Getting recommendations for seed video: {video_id}...")
        
        # get_watch_playlist simulates "Start Radio"
        watch_playlist = yt.get_watch_playlist(videoId=video_id, limit=limit)
        
        if not watch_playlist or 'tracks' not in watch_playlist:
            logger.warning("No tracks returned in watch playlist.")
            return []
            
        tracks = watch_playlist['tracks']
        logger.info(f"Received {len(tracks)} raw tracks from algorithm.")

        parsed_recs = []
        for track in tracks[:limit]:
            try:
                # Skip the seed song itself if it appears first (often does)
                if track.get('videoId') == video_id:
                    continue

                title = track.get('title')
                vid = track.get('videoId')
                
                if not vid or not title:
                    continue
                    
                artists = track.get('artists', [])
                artist_name = artists[0]['name'] if artists else "Unknown"
                
                album_info = track.get('album') # Might be None
                album_name = album_info.get('name') if album_info else "Single/Unknown"
                
                parsed_recs.append({
                    "videoId": vid,
                    "title": title,
                    "artist": artist_name,
                    "album": album_name,
                    "duration": track.get('length', '') # Watch playlist uses 'length' not 'duration'
                })
            except Exception as e:
                logger.warning(f"Error parsing rec track: {e}")
                continue
                
        return parsed_recs

    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        return []
