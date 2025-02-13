import yandex_music

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
        return "Song not found"

# search = input("Search for song: ")
# link = get_song_link(search)
# print(link)
