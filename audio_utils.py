import os
import yt_dlp
from pydub import AudioSegment

def get_raw_file(link):
    output_path = "output"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'noplaylist': True,
        'retries': 3,  # Retry 3 times
        'socket_timeout': 30,  # Increase timeout to 30 seconds
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(link, download=True)
            file_path = ydl.prepare_filename(info).replace('.webm', '.mp3')
            return file_path
        except yt_dlp.utils.DownloadError as e:
            print(f"Download error: {e}")
            return None

    # Convert to raw MP3
    # audio = AudioSegment.from_file(file_path)
    # raw_mp3_path = file_path.replace('.mp3', '_raw.mp3')
    # audio.export(raw_mp3_path, format="mp3")
    # return raw_mp3_path
