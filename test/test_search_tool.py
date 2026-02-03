import sys
import os

# Add project root to path so we can import tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.search_tool import search_song

def main():
    print("Testing tools/search_tool.py...")
    
    query = "Bohemian Rhapsody Queen"
    print(f"Searching for: '{query}'")
    
    results = search_song(query)
    
    if not results:
        print("❌ No results found. Test Failed.")
        return

    print(f"✅ Search successful. Found {len(results)} results.")
    
    first = results[0]
    print("\nFirst Result:")
    print(f"  Title: {first.get('title')}")
    print(f"  Artist: {first.get('artist')}")
    print(f"  Album: {first.get('album')}")
    print(f"  Duration: {first.get('duration')}")
    print(f"  Video ID: {first.get('videoId')}")
    
    # Validation
    required_keys = ["videoId", "title", "artist", "album", "duration"]
    missing_keys = [key for key in required_keys if key not in first]
    
    if missing_keys:
        print(f"❌ Missing keys in result: {missing_keys}")
    else:
        print("\n✅ Data structure looks correct.")

if __name__ == "__main__":
    main()
