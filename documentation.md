# Flask YouTube Downloader Application
# Overview
This Flask-based web application enables users to download videos, music, and playlists from YouTube. It supports downloading audio in MP3 format or videos in MP4 format, along with their associated thumbnails. The application features various routes for handling video, music, and playlist downloads, as well as viewing and playing content directly from the server.

# Requirements

Flask: Web framework for creating the app
yt-dlp: A powerful command-line tool for downloading videos and audio from YouTube.
Werkzeug: Utility functions for secure filename handling and joining paths.
Subprocess: For running shell commands to invoke yt-dlp and handle downloads.
ThreadPoolExecutor: For handling concurrent downloads via threading.

# Key Folders
VIDEOS_FOLDER: Stores downloaded videos. Default: ./videos
MUSIC_FOLDER: Stores downloaded music. Default: ./musique

# Functions
1. sanitize_filename(filename)
Cleans filenames by removing illegal characters to ensure file safety during saving.

2. download_audio_with_ytdlp(url, output_path='./musique')
Downloads a single audio file from a YouTube URL. It retrieves information about the audio file, downloads it in MP3 format, downloads the associated thumbnail, and creates a views.txt file to track the number of views.

3. download_music_playlist_with_ytdlp(playlist_url, base_output_path='./musique')
Downloads a playlist of music from YouTube in MP3 format. Each track is downloaded into its own folder, which includes the MP3 file, thumbnail, and a views.txt file.

4. download_video_with_ytdlp(url, output_path='.')
Downloads a single video from a YouTube URL. The video is saved as an MP4 file along with its thumbnail, and a views.txt file is created to store the number of views.

5. download_playlist_with_ytdlp(playlist_url, base_output_path='./videos')
Downloads a YouTube video playlist in MP4 format. Each video in the playlist is stored in a separate folder with the video file, thumbnail, and a views.txt file. The videos are organized and indexed according to their playlist position.

# Routes
1. /
Renders the homepage (index.html).

2. /download
Handles video and playlist downloads. The user submits a YouTube URL, and the appropriate download function is executed in a separate thread using ThreadPoolExecutor.

3. /watch
Lists all downloaded videos and playlists for users to watch. Displays the number of views for each item.

4. /play_video/<video>
Plays a specific video, increments its view count, and renders play_video.html.

5. /play_playlist/<playlist>
Plays a video playlist, showing each video within the playlist in order. Renders play_playlist.html.

6. /download_music
Handles music and music playlist downloads in a manner similar to /download, but stores the files in the MUSIC_FOLDER.

7. /listen_music
Displays downloaded music and music playlists, along with their associated thumbnails and view counts.

8. /play_music/<music>
Plays an individual music file, increments its view count, and renders play_music.html.

9. /play_music_playlist/<playlist>
Plays all songs from a music playlist, optionally in a shuffled order, and renders play_music_playlist.html.

10. /thumbnail/<path:filename>
Serves thumbnail images for videos and music.

11. /video/<path:filename> and /music/<path:filename>
Serve video and music files directly from their respective directories.

12. /download_file/<path:filename>
Allows users to download an individual music file from a music playlist.

13. /download_music_playlist_all/<string:playlist>
Displays all MP3 files within a playlist and allows users to download the entire playlist.

Concurrency
The app uses a ThreadPoolExecutor to handle multiple download requests concurrently without blocking the main application.

