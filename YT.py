from ytmusicapi import YTMusic

def get_song_link(search: str):
    # Initialize the YTMusic API
    ytmusic = YTMusic()

    # Search for the song
    search_results = ytmusic.search(query=search, filter='songs')

    # Check if there are any results
    if search_results:
        # Get the first result
        song = search_results[0]
        # Construct the song link
        song_link = f"https://music.youtube.com/watch?v={song['videoId']}"
        return song_link
    else:
        return "Song not found."
    

# search = input("Search for song: ")
# link = get_song_link(search)
# print(f"Link to the song: {link}")

