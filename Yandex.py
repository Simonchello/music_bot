import yandex_music
import re

def get_song_link(search: str):
    # Initialize the client
    client = yandex_music.Client().init()

    # Search for the song
    search_results = client.search(search)

    # Check if there are any results
    if search_results.tracks:
        # Get the first track from the search results
        track = search_results.tracks.results[0]
        
        # Construct the link to the song
        song_link = f"https://music.yandex.ru/album/{track.albums[0].id}/track/{track.id}"
        return song_link
    else:
        return "Song not found."

def get_song_info_from_url(url):
    # Check if the URL is a Yandex Music link
    if not url.startswith("https://music.yandex.ru/"):
        return "Not Yandex music link"
    
    # Initialize the client
    client = yandex_music.Client().init()
    
    # Extract track ID from URL using regex
    track_id_match = re.search(r'track/(\d+)', url)
    
    if not track_id_match:
        return "Invalid Yandex Music URL"
    
    track_id = track_id_match.group(1)
    
    try:
        # Get track info
        track = client.tracks([track_id])[0]
        
        # Get artist names (there can be multiple artists)
        artists = [artist.name for artist in track.artists]
        artist_names = ", ".join(artists)
        
        # Get track title
        track_name = track.title
        
        return {
            "artist": artist_names,
            "title": track_name
        }
    except Exception as e:
        return f"Error retrieving song info: {str(e)}"

# search = input("Search for song: ")
# link = get_song_link(search)
# print(link)

# # Example usage
# url = input("URL for song: ")
# song_info = get_song_info_from_url(url)
# print(f"Artist: {song_info['artist']}")
# print(f"Song: {song_info['song']}")
