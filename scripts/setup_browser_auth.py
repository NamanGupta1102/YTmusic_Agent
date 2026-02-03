from ytmusicapi import YTMusic
import json
import re

def parse_curl_and_save(curl_file_path='curl.txt', output_path='browser.json'):
    print(f"Reading {curl_file_path}...")
    
    try:
        with open(curl_file_path, 'r', encoding='utf-8') as f:
            curl_content = f.read()
    except FileNotFoundError:
        print(f"Error: {curl_file_path} not found.")
        return

    headers = {}
    
    # 1. Regex to find headers in curl command
    # Matches -H 'Key: Value' or -H "Key: Value" or -H "Key:Value"
    # Capture Group 1: Key, Group 2: Value
    header_matches = re.findall(r"-H\s+['\"]([^:]+):\s*([^'\"]+)['\"]", curl_content)
    
    for key, value in header_matches:
        # Lowercase keys standardizes them for ytmusicapi
        # Strip whitespace/newlines which cause "Invalid character" errors in requests
        clean_key = key.lower().strip()
        clean_value = value.strip()
        headers[clean_key] = clean_value

    # 2. Extract cookies if separate flag used (-b or --cookie)
    # usually modern chrome curl puts cookie in -H 'cookie: ...' which the above catches
    cookie_matches = re.findall(r"(?:-b|--cookie)\s+['\"]([^'\"]+)['\"]", curl_content)
    if cookie_matches and 'cookie' not in headers:
        headers['cookie'] = cookie_matches[0]
        print("Found cookie via -b/--cookie flag.")
        
    # 3. Clean up compression headers that might break python requests
    # (ytmusicapi usually handles this via requests, but good to be safe)
    if 'accept-encoding' in headers:
        del headers['accept-encoding']

    # 4. Filter for strict Keys if we want to avoid polluting with "sec-ch-ua" etc?
    # Actually, sending ALL captured headers is usually safest to mimic the browser.
    
    # Check for critical headers
    if 'cookie' not in headers:
        print("❌ Error: 'cookie' header not found. Please ensure you copied the full curl command including cookies.")
        return
    if 'authorization' not in headers:
        print("⚠️ Warning: 'authorization' header (SAPISIDHASH) not found. Some actions might fail.")

    print(f"Found {len(headers)} headers.")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(headers, f, indent=4)
        
    print(f"✅ Success! Saved to {output_path}")

if __name__ == "__main__":
    parse_curl_and_save()
