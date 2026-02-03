import logging

logger = logging.getLogger(__name__)

class SessionState:
    def __init__(self):
        self.cart = []  # List of dictionaries: {videoId, title, artist}
        
    def add_song(self, song: dict) -> str:
        """
        Adds a song to the cart if it's not already there.
        Args:
            song: Dict containing 'videoId', 'title', 'artist'
        Returns:
            Message indicating result.
        """
        # Check for duplicates using videoId
        if any(s['videoId'] == song['videoId'] for s in self.cart):
            return f"'{song['title']}' is already in your cart."
            
        self.cart.append(song)
        logger.info(f"Added to cart: {song['title']} ({song['videoId']})")
        return f"Added '{song['title']}' by {song['artist']} to your cart. (Total: {len(self.cart)})"

    def remove_song(self, identifier: str) -> str:
        """
        Removes a song by title (fuzzy match) or videoId.
        """
        identifier = identifier.lower().strip()
        
        # Try finding by index if user says "remove number 1"
        # (This logic might be handled by LLM converting to ID, but simple fallback helps)
        
        for i, song in enumerate(self.cart):
            if song['videoId'] == identifier or identifier in song['title'].lower():
                removed = self.cart.pop(i)
                return f"Removed '{removed['title']}' from cart."
                
        return f"Could not find a song matching '{identifier}' in your cart."

    def get_cart(self) -> list[dict]:
        return self.cart

    def get_cart_display(self) -> str:
        """String representation for the LLM/User."""
        if not self.cart:
            return "Your cart is empty."
            
        output = "Current Cart:\n"
        for i, song in enumerate(self.cart, 1):
            output += f"{i}. {song['title']} - {song['artist']}\n"
        return output

    def clear(self):
        self.cart = []
