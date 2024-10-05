# YouTube Playlist Downloader and Player Application :

This is a Flask-based web application that allows users to download and play YouTube videos and playlists, as well as music. The app supports video thumbnail downloads, playlist organization, and track view counters.

/!\ Note that this is a non-serious application, made for me and for people that would like to use it ! This has and will have a lot of bugs and isn't perfect ! /!\


# Features:

Download YouTube Playlists (Video/Audio): Download entire YouTube playlists with options to store each video/music in separate folders.
Thumbnail Handling: Automatically download and rename video thumbnails to thumbnail.jpg.
Playlist and Music Views: Track the number of views for each video/music and display it on the user interface.
Video and Music Streaming: Watch videos or listen to music from downloaded YouTube playlists directly in the browser.
Responsive UI: Adapted to different devices, including desktops and mobile phones.
Music-Specific Functionality: Separate routes and logic for downloading and listening to music playlists, stored in a dedicated music folder.
Flask Integration: Easily configurable and customizable routes for serving music, videos, and playlists.

# Installation : 

Open a cmd prompt in the project location, and type in "pip install requirements.txt" to install the librairies (install python first)
Run the program by putting "python index.py" on the same cmd.

Access the application by navigating to http://127.0.0.1:17000 in your browser.


# Usage:


Downloading Playlists
Enter the playlist URL on the home page.
The app will download the videos/music to their respective folders (videos or music) and create subfolders for each entry.
Thumbnails are automatically renamed to thumbnail.jpg and view counters (views.txt) are created in each folder.
Watching Videos
Navigate to the "Watch Videos" section.
Browse through the available downloaded playlists.
Click on a video to watch it in the browser, where you can also see the number of views.
Listening to Music
Navigate to the "Listen to Music" section.
Browse through the available music playlists.
Click on a song to play it in the browse.


# Directory Structure:

.
├── index.py                # Main application logic

├── templates/              # HTML templates

├── videos/                 # Directory for downloaded videos

├── musique/                  # Directory for downloaded music

└── requirements.txt        # Python dependencies


# Routes:


/: Home page with options to download or view content.
/download_playlist: Route to handle downloading YouTube playlists.
/watch: Browse and watch videos.
/play_video/<path:video>: Watch a specific video.
/listen_music: Browse and listen to music.
/play_music/<path:music>: Listen to a specific music track.
/serve_video/<filename>: Serve video files.
/serve_music/<filename>: Serve audio files.
Technologies
Backend: Flask, yt-dlp, FFmpeg
Frontend: HTML, CSS, JavaScript
Database: Simple file-based system (views tracked via views.txt files)

# Contribution
Feel free to fork this repository, submit issues, or make pull requests to contribute to this project.


# Contact:
For further information or inquiries, please contact:
Email: gazerbim@gmail.com

Demo video (in french) at https://www.youtube.com/watch?v=Gn_FvaHofW8
