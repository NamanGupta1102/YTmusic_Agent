import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.recommendation_tool import get_recommendations
from tools.search_tool import search_song

def main():
    print("Testing tools/recommendation_tool.py...")
    
    # 1. Get a seed ID
    seed_query = "Blinding Lights The Weeknd"
    print(f"Finding seed song for: '{seed_query}'")
    search_res = search_song(seed_query, limit=1)
    
    if not search_res:
        print("❌ Could not find seed song.")
        return
        
    seed_id = search_res[0]['videoId']
    print(f"Seed ID: {seed_id} ({search_res[0]['title']})")
    
    # 2. Get Recommendations
    print("\nFetching recommendations...")
    recs = get_recommendations(seed_id, limit=5)
    
    if not recs:
        print("❌ No recommendations returned.")
        return
        
    print(f"✅ Success! Got {len(recs)} recommendations.")
    
    print("\nTop Recommendation:")
    first = recs[0]
    print(f"  Title: {first.get('title')}")
    print(f"  Artist: {first.get('artist')}")
    print(f"  Album: {first.get('album')}")
    
    required = ['videoId', 'title', 'artist']
    missing = [k for k in required if k not in first]
    if missing:
        print(f"❌ Missing keys: {missing}")
    else:
        print("✅ Data structure valid.")

if __name__ == "__main__":
    main()
