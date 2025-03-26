import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

# Read credentials from files
def read_credentials():
    try:
        with open('client_id', 'r') as f:
            client_id = f.read().strip()
        with open('client_secret', 'r') as f:
            client_secret = f.read().strip()
        return client_id, client_secret
    except FileNotFoundError:
        print("Error: client_id or client_secret file not found.")
        return None, None

def get_spotify_client():
    client_id, client_secret = read_credentials()
    if not client_id or not client_secret:
        raise ValueError("Missing Spotify credentials")
    
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song_link(search: str):
    try:
        # Initialize the Spotify client
        sp = get_spotify_client()
        
        # Search for the track
        results = sp.search(q=search, type='track', limit=1)
        
        # Check if there are any results
        if results['tracks']['items']:
            # Get the first result
            track = results['tracks']['items'][0]
            # Return the Spotify URL
            return track['external_urls']['spotify']
        else:
            return "Song not found."
    except Exception as e:
        return f"Error searching for song: {str(e)}"

def get_song_info_from_url(url: str):
    try:
        # Check if the URL is a Spotify link
        if not url.startswith("https://open.spotify.com/"):
            return "Not a Spotify music link"
        
        # Initialize the Spotify client
        sp = get_spotify_client()
        
        # Extract track ID from URL using regex
        track_id_match = re.search(r'track/([a-zA-Z0-9]+)', url)
        
        if not track_id_match:
            return "Invalid Spotify URL"
        
        track_id = track_id_match.group(1)
        
        # Get track info
        track = sp.track(track_id)
        
        # Get artist name (first artist if multiple)
        artist = track['artists'][0]['name']
        
        # Get track title
        title = track['name']
        
        return {
            "artist": artist,
            "title": title
        }
    except Exception as e:
        return f"Error retrieving song info: {str(e)}"

# Example usage (commented out)
# search_term = input("Search for the song: ")
# print(get_song_link(search_term))
# 
# url = input("URL for song: ")
# song_info = get_song_info_from_url(url)
# print(song_info)