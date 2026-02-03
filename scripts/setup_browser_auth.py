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

    # Extract headers using regex
    # Matches -H 'Key: Value' or -H "Key: Value"
    headers = {}
    
    # Regex to find headers in curl command
    # Look for -H followed by quote, key, colon, value, quote
    header_matches = re.findall(r"-H\s+['\"]([^:]+):\s+([^'\"]+)['\"]", curl_content)
    
    if not header_matches:
        print("No headers found in curl.txt. Make sure it follows standard curl format.")
        return

    for key, value in header_matches:
        headers[key.lower()] = value

    # Extract cookies (-b or --cookie)
    cookie_matches = re.findall(r"(?:-b|--cookie)\s+['\"]([^'\"]+)['\"]", curl_content)
    if cookie_matches:
        headers['cookie'] = cookie_matches[0]
        print("Found cookie via -b/--cookie flag.")

    # Check for critical headers
    if 'cookie' not in headers and 'authorization' not in headers:
         print("Warning: Neither 'cookie' nor 'authorization' found. Auth might fail.")

    # ytmusicapi expects a JSON file with these headers
    # We can just save the headers dict provided we have the right ones.
    # Usually ytmusicapi wants the full headers dict.
    
    print(f"Found {len(headers)} headers.")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(headers, f, indent=4)
        
    print(f"Success! Saved to {output_path}")

if __name__ == "__main__":
    parse_curl_and_save()
