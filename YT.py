from ytmusicapi import YTMusic
import re

def get_song_link(search: str):
    # Initialize the YTMusic API
    ytmusic = YTMusic()

    # Search for the song
    search_results = ytmusic.search(query=search, filter='songs')

    # Check if there are any results
    if search_results:
        # Get the first result
        song = search_results[0]
        # print(search_results)
        # Construct the song link
        song_link = f"https://music.youtube.com/watch?v={song['videoId']}"
        return song_link
    else:
        return "Song not found."

def get_song_info_from_url(url: str):
    # Extract the video ID from the URL
    video_id_match = re.search(r"watch\?v=(\S{11})", url)
    if not video_id_match:
        return "Invalid YouTube Music URL"
    
    video_id = video_id_match.group(1)
    
    # Initialize the YTMusic API
    ytmusic = YTMusic()
    
    # Get song info from video ID
    try:
        # Use get_watch_playlist instead of get_song
        results = ytmusic.get_watch_playlist(videoId=video_id)
        
        if 'tracks' in results and len(results['tracks']) > 0:
            track = results['tracks'][0]
            
            # Extract title
            title = track.get('title', 'Unknown Title')
            
            # Extract artist
            artists = track.get('artists', [])
            artist = artists[0]['name'] if artists else 'Unknown Artist'
            
            return {
                'title': title,
                'artist': artist
            }
        else:
            return {'title': 'Unknown Title', 'artist': 'Unknown Artist'}
    except Exception as e:
        return f"Error retrieving song info: {str(e)}"

# Example usage
# search = input("Search for song: ")
# link = get_song_link(search)
# print(f"Link to the song: {link}")

# # Example of getting song info from URL
# link = input("URL to the YT song: " )
# if link != "Song not found.":
#     song_info = get_song_info_from_url(link)
#     print(f"Song information: {song_info}")

