from flask import Flask, render_template, request, send_from_directory, redirect, url_for, abort, flash
import os
import random
from werkzeug.utils import secure_filename
import subprocess
import re
import json
import shutil
import threading
import concurrent.futures
from werkzeug.utils import safe_join
from urllib.parse import unquote
import random
import urllib.parse

executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

app = Flask(__name__)

VIDEOS_FOLDER = './videos'
app.config['VIDEOS_FOLDER'] = VIDEOS_FOLDER
MUSIC_FOLDER = './musique'
app.config['MUSIC_FOLDER'] = MUSIC_FOLDER


def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_audio_with_ytdlp(url, output_path='./musique'):
    print("Téléchargement de la musique lancé")
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Récupérer les informations sur la vidéo avec les commandes direct
        info_command = [
            "yt-dlp",
            "--dump-json",
            "--extract-audio",
            "--audio-format", "mp3",
            url
        ]
        result = subprocess.run(info_command, capture_output=True, text=True, check=True)
        audio_info = json.loads(result.stdout)

        audio_title = sanitize_filename(audio_info['title'])
        audio_folder = os.path.join(output_path, audio_title)

        if not os.path.exists(audio_folder):
            os.makedirs(audio_folder)

        # Télécharger l'audio avec la commande prompt
        audio_command = [
            "yt-dlp",
            "--verbose",
            "-x",
            "--audio-format", "mp3",
            url,
            "-o", os.path.join(audio_folder, '%(title)s.%(ext)s')
        ]
        subprocess.run(audio_command, check=True)

        # Télécharger la miniature
        thumbnail_command = [
            "yt-dlp",
            "--write-thumbnail",
            "--skip-download",
            url,
            "-o", os.path.join(audio_folder, "thumbnail")
        ]
        subprocess.run(thumbnail_command, check=True)

        # Renommer la miniature en thumbnail.jpg
        for file in os.listdir(audio_folder):
            if file.startswith("thumbnail"):
                thumbnail_ext = os.path.splitext(file)[1]
                os.rename(os.path.join(audio_folder, file), os.path.join(audio_folder, "thumbnail.jpg"))
                break

        # Créer un fichier de vues
        with open(os.path.join(audio_folder, "views.txt"), "w") as f:
            f.write("0")

        print(f"Téléchargement de la musique depuis {url} terminé dans {audio_folder}.")

    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de yt-dlp : {e}")
    except Exception as e:
        print(f"Erreur générale : {e}")



def download_music_playlist_with_ytdlp(playlist_url, base_output_path='./musique'):
    print("Téléchargement de la playlist de musique lancé")
    try:
        # Récupérer les infos de la playlist toujours avec les commandes
        info_command = [
            "yt-dlp",
            "--flat-playlist",
            "--dump-json",
            playlist_url
        ]
        result = subprocess.run(info_command, capture_output=True, text=True, check=True)
        playlist_info = result.stdout.splitlines()[0]

        playlist_data = json.loads(playlist_info)
        print(playlist_data)
        playlist_title = sanitize_filename(playlist_data.get('playlist', 'Unknown_Playlist'))

        playlist_path = os.path.join(base_output_path, playlist_title)
        if not os.path.exists(playlist_path):
            os.makedirs(playlist_path)

        # Commande pour télécharger les musiques en mp3 avec leurs miniatures
        download_command = [
            "yt-dlp",
            "--verbose",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "--write-thumbnail",
            playlist_url,
            "-o", os.path.join(playlist_path, '%(playlist_index)s-%(title)s/%(title)s.%(ext)s')
        ]

        subprocess.run(download_command, check=True)

        # Organiser les fichiers et créer views.txt pour chaque musique (meme si inutile il faudrait l'enlever)
        for item in os.listdir(playlist_path):
            item_path = os.path.join(playlist_path, item)
            if os.path.isdir(item_path):
                for file in os.listdir(item_path):
                    if file.endswith(".jpg") or file.endswith(".webp"):
                        os.rename(os.path.join(item_path, file), os.path.join(item_path, "thumbnail.jpg"))
                    elif file.endswith(".mp3"):
                        pass
                    else:
                        os.remove(os.path.join(item_path, file))

                with open(os.path.join(item_path, "views.txt"), "w") as f:
                    f.write("0")

        print(f"Téléchargement de la playlist '{playlist_title}' terminé dans {playlist_path}.")

    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de yt-dlp : {e}")
    except Exception as e:
        print(f"Erreur générale : {e}")




def download_video_with_ytdlp(url, output_path='.'):
    print("Telechargement de la vidéo lancé")
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Get video info
        info_command = [
            "yt-dlp",
            "--dump-json",
            url
        ]
        result = subprocess.run(info_command, capture_output=True, text=True, check=True)
        video_info = json.loads(result.stdout)

        video_title = sanitize_filename(video_info['title'])
        video_folder = os.path.join(output_path, video_title)

        if not os.path.exists(video_folder):
            os.makedirs(video_folder)

        # télécharger video
        video_command = [
            "yt-dlp",
            "--verbose",
            "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "--merge-output-format", "mp4",
            url,
            "-o", os.path.join(video_folder, '%(title)s.%(ext)s')
        ]
        subprocess.run(video_command, check=True)

        # télécharger miniature
        thumbnail_command = [
            "yt-dlp",
            "--write-thumbnail",
            "--skip-download",
            url,
            "-o", os.path.join(video_folder, "thumbnail")
        ]
        subprocess.run(thumbnail_command, check=True)

        # Rename thumbnail to .jpg
        for file in os.listdir(video_folder):
            if file.startswith("thumbnail"):
                thumbnail_ext = os.path.splitext(file)[1]
                os.rename(os.path.join(video_folder, file), os.path.join(video_folder, "thumbnail.jpg"))
                break

        # Create views file
        with open(os.path.join(video_folder, "views.txt"), "w") as f:
            f.write("0")

        print(f"Téléchargement de la vidéo depuis {url} terminé dans {video_folder}.")

    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de yt-dlp : {e}")
    except Exception as e:
        print(f"Erreur générale : {e}")


def download_playlist_with_ytdlp(playlist_url, base_output_path='./videos'):
    print("Téléchargement de la playlist lancé")
    try:
        # Obtenir les informations de la playlist
        info_command = [
            "yt-dlp",
            "--flat-playlist",
            "--dump-json",
            playlist_url
        ]
        result = subprocess.run(info_command, capture_output=True, text=True, check=True)
        playlist_info = result.stdout.splitlines()

        playlist_size = len(playlist_info)

        playlist_data = json.loads(playlist_info[0])
        print(playlist_data)
        playlist_title = sanitize_filename(playlist_data.get('playlist', 'Unknown_Playlist'))

        playlist_path = os.path.join(base_output_path, playlist_title)
        if not os.path.exists(playlist_path):
            os.makedirs(playlist_path)

        # Modifier la commande de téléchargement
        download_command = [
            "yt-dlp",
            "--verbose",
            "--playlist-reverse",
            "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "--merge-output-format", "mp4",
            "--write-thumbnail",
            playlist_url,
            "-o", os.path.join(playlist_path, f'%(playlist_index)s-%(title)s/%(title)s.%(ext)s')
        ]

        subprocess.run(download_command, check=True)

        # Renommer les dossiers après le téléchargement
        for item in os.listdir(playlist_path):
            item_path = os.path.join(playlist_path, item)
            if os.path.isdir(item_path):
                old_index = int(item.split('-')[0])
                new_index = playlist_size - old_index + 1
                new_name = f"{new_index:03d}-{'-'.join(item.split('-')[1:])}"
                os.rename(item_path, os.path.join(playlist_path, new_name))

        # Organiser les fichiers et créer views.txt pour chaque vidéo
        for item in os.listdir(playlist_path):
            item_path = os.path.join(playlist_path, item)
            if os.path.isdir(item_path):
                for file in os.listdir(item_path):
                    if file.endswith(".jpg") or file.endswith(".webp") or file.endswith(".png"):
                        # Renommer la miniature en thumbnail.jpg
                        os.rename(os.path.join(item_path, file), os.path.join(item_path, "thumbnail.jpg"))
                    elif file.endswith(".mp4"):
                        pass
                    else:
                        os.remove(os.path.join(item_path, file))

                with open(os.path.join(item_path, "views.txt"), "w") as f:
                    f.write("0")

        print(f"Téléchargement de la playlist '{playlist_title}' terminé dans {playlist_path}.")

    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de yt-dlp : {e}")
    except Exception as e:
        print(f"Erreur générale : {e}")

def sanitize_filename(filename):
    # Implémentez cette fonction pour nettoyer les noms de fichiers si nécessaire
    return filename  # Ceci est une implémentation simplifiée


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == 'POST':
        url = request.form['url']

        # Démarrer un thread pour le téléchargement
        if 'playlist' in url:
            executor.submit(download_playlist_with_ytdlp, url, app.config['VIDEOS_FOLDER'])
        else:
            executor.submit(download_video_with_ytdlp, url, app.config['VIDEOS_FOLDER'])

        return redirect(url_for('download'))

    return render_template('download.html')


@app.route('/watch')
def watch():
    search_query = request.args.get('search', '').lower()
    videos = []
    playlists = []

    for item in os.listdir(app.config['VIDEOS_FOLDER']):
        item_path = os.path.join(app.config['VIDEOS_FOLDER'], item)
        if os.path.isdir(item_path):
            if any(file.endswith('.mp4') for file in os.listdir(item_path)):
                # This is a single video
                if not search_query or search_query in item.lower():
                    views_file_path = os.path.join(item_path, "views.txt")

                    # Créer views.txt s'il n'existe pas
                    if not os.path.exists(views_file_path):
                        with open(views_file_path, "w") as f:
                            f.write("0")  # Initialise les vues à 0

                    with open(views_file_path, "r") as f:
                        views = int(f.read().strip())
                    videos.append({'name': item, 'views': views})
            else:
                # This is a playlist
                if not search_query or search_query in item.lower():
                    # Utiliser un fallback pour éviter l'exception StopIteration
                    first_video = next(
                        (subdir for subdir in os.listdir(item_path) if os.path.isdir(os.path.join(item_path, subdir))),
                        None)

                    # Vérifier que `first_video` n'est pas `None`
                    if first_video:
                        playlists.append({'name': item, 'first_video': first_video})
                    else:
                        print(f"Aucun sous-dossier trouvé dans la playlist : {item}")

    if 'random' in request.args:
        if videos:
            return redirect(url_for('play_video', video=random.choice(videos)['name']))
        elif playlists:
            return redirect(url_for('play_playlist', playlist=random.choice(playlists)['name']))

    random.shuffle(videos)
    random.shuffle(playlists)

    return render_template('watch.html', videos=videos, playlists=playlists)


@app.route('/play_video/<video>')
def play_video(video):
    video_path = os.path.join(app.config['VIDEOS_FOLDER'], video)
    views_file = os.path.join(video_path, "views.txt")

    # Increment views
    with open(views_file, "r+") as f:
        views = int(f.read().strip())
        views += 1
        f.seek(0)
        f.write(str(views))
        f.truncate()

    video_file = next(f for f in os.listdir(video_path) if f.endswith('.mp4'))
    return render_template('play_video.html', video=video, video_file=video_file, views=views)


@app.route('/thumbnail/<path:filename>')
def serve_thumbnail(filename):
    # Vérifier d'abord dans le dossier des vidéos
    video_path = safe_join(app.config['VIDEOS_FOLDER'], filename)
    if os.path.exists(video_path):
        return send_from_directory(app.config['VIDEOS_FOLDER'], filename)

    # Si non trouvé, vérifier dans le dossier des musiques
    music_path = safe_join(app.config['MUSIC_FOLDER'], filename)
    if os.path.exists(music_path):
        return send_from_directory(app.config['MUSIC_FOLDER'], filename)

    # Si toujours pas trouvé, renvoyer une erreur 404
    return "Thumbnail not found", 404

@app.route('/play_playlist/<playlist>')
def play_playlist(playlist):
    playlist_path = os.path.join(app.config['VIDEOS_FOLDER'], playlist)
    videos = []
    for item in sorted(os.listdir(playlist_path), reverse=False):
        item_path = os.path.join(playlist_path, item)
        if os.path.isdir(item_path):
            mp4_files = [f for f in os.listdir(item_path) if f.endswith('.mp4')]
            if mp4_files:
                video_file = mp4_files[0]
                views_file = os.path.join(item_path, "views.txt")
                if os.path.exists(views_file):
                    with open(views_file, "r") as f:
                        views = int(f.read().strip())
                else:
                    views = 0

                thumbnail_path = os.path.join(item_path, "thumbnail.jpg")
                if os.path.exists(thumbnail_path):
                    thumbnail_url = url_for('serve_thumbnail', filename=f"{playlist}/{item}/thumbnail.jpg")
                else:
                    thumbnail_url = url_for('static', filename='default_thumbnail.jpg')

                videos.append({
                    'name': item,
                    'file': video_file,
                    'views': views,
                    'thumbnail': thumbnail_url
                })

    if not videos:
        #flash("Aucune vidéo trouvée dans cette playlist.", "warning")
        return redirect(url_for('watch'))

    return render_template('play_playlist.html', playlist=playlist, videos=videos)


@app.route('/video/<path:filename>')
def serve_video(filename):
    return send_from_directory(app.config['VIDEOS_FOLDER'], filename)

@app.route('/download_music', methods=['GET', 'POST'])
def download_music():
    if request.method == 'POST':
        url = request.form['url']

        # Démarrer un thread pour le téléchargement
        if 'playlist' in url:
            executor.submit(download_music_playlist_with_ytdlp, url, app.config['MUSIC_FOLDER'])
        else:
            executor.submit(download_audio_with_ytdlp, url, app.config['MUSIC_FOLDER'])

        return redirect(url_for('download_music'))

    return render_template('download_music.html')


@app.route('/listen_music')
def listen_music():
    search_query = request.args.get('search', '').lower()
    music_files = []
    playlists = []

    for item in os.listdir(app.config['MUSIC_FOLDER']):
        item_path = os.path.join(app.config['MUSIC_FOLDER'], item)
        if os.path.isdir(item_path):
            if "views.txt" in os.listdir(item_path):
                # C'est une musique individuelle
                if not search_query or search_query in item.lower():
                    views_file_path = os.path.join(item_path, "views.txt")
                    with open(views_file_path, "r") as f:
                        views = int(f.read().strip())
                    mp3_file = next((f for f in os.listdir(item_path) if f.endswith('.mp3')), None)
                    if mp3_file:
                        music_files.append({
                            'name': item,
                            'mp3_file': os.path.join(item, mp3_file),
                            'views': views,
                            'thumbnail': url_for('serve_thumbnail', filename=f"{item}/thumbnail.jpg")
                        })
            else:
                # C'est une playlist
                if not search_query or search_query in item.lower():
                    playlist_views = sum(int(open(os.path.join(item_path, subitem, "views.txt"), "r").read().strip())
                                         for subitem in os.listdir(item_path)
                                         if os.path.isdir(os.path.join(item_path, subitem))
                                         and "views.txt" in os.listdir(os.path.join(item_path, subitem)))

                    # Trouver la première chanson de la playlist pour utiliser son image
                    first_song = next((subitem for subitem in os.listdir(item_path)
                                       if os.path.isdir(os.path.join(item_path, subitem))), None)

                    thumbnail_url = url_for('static', filename='default_thumbnail.jpg')
                    if first_song:
                        thumbnail_path = os.path.join(item_path, first_song, "thumbnail.jpg")
                        if os.path.exists(thumbnail_path):
                            thumbnail_url = url_for('serve_thumbnail', filename=f"{item}/{first_song}/thumbnail.jpg")

                    playlists.append({
                        'name': item,
                        'views': playlist_views,
                        'thumbnail': thumbnail_url
                    })

    random.shuffle(playlists)
    random.shuffle(music_files)
    return render_template('listen_music.html', music_files=music_files, playlists=playlists)


@app.route('/play_music/<music>')
def play_music(music):
    # Construire le chemin absolu du dossier de la musique
    music_path = os.path.join(app.config['MUSIC_FOLDER'], music)
    print(music)
    print(music_path)
    music_path = "./musique/"+music.split("\\")[0]
    print(music_path)
    music = music.split("\\")[0]

    # Vérifier si le dossier de la musique existe
    if os.path.exists(music_path) and os.path.isdir(music_path):
        # Vérifier le fichier de vues dans le dossier de la musique
        views_file = os.path.join(music_path, "views.txt")

        # Initialiser ou mettre à jour le compteur de vues
        if os.path.exists(views_file):
            with open(views_file, "r+") as f:
                views = int(f.read().strip())
                views += 1
                f.seek(0)
                f.write(str(views))
                f.truncate()
        else:
            views = 0  # Si le fichier de vues n'existe pas, on initialise à 0

        # Trouver le fichier .mp3 dans le dossier de la musique (pas dans les sous-dossiers)
        mp3_file = next((f for f in os.listdir(music_path) if f.endswith('.mp3')), None)

        if not mp3_file:
            return "Fichier MP3 introuvable", 404

        # Construire le chemin relatif pour le rendu dans le template
        mp3_file_path = os.path.join(music, mp3_file).replace('\\', '/')

        # Retourner le template avec le fichier MP3 et les vues
        return render_template('play_music.html', music=music, mp3_file=mp3_file_path, views=views)

    return "Dossier de musique introuvable", 404


import random


@app.route('/play_music_playlist/<playlist>')
@app.route('/play_music_playlist/<playlist>/<shuffle>')
def play_music_playlist(playlist, shuffle=False):
    playlist_path = os.path.join(app.config['MUSIC_FOLDER'], playlist)
    if os.path.exists(playlist_path):
        music_files = []
        for item in os.listdir(playlist_path):
            item_path = os.path.join(playlist_path, item)
            if os.path.isdir(item_path):
                views_file_path = os.path.join(item_path, "views.txt")
                print(views_file_path)
                mp3_file = next((f for f in os.listdir(item_path) if f.endswith('.mp3')), None)
                if mp3_file:
                    music_files.append({
                        'name': item,
                        'mp3_file': os.path.join(playlist, item, mp3_file),
                    })

        # Mélange la playlist si shuffle est activé
        if shuffle:
            random.shuffle(music_files)

        return render_template('play_music_playlist.html', playlist=playlist, music_files=music_files, shuffle=shuffle)

    return "Playlist non trouvée", 404


@app.route('/music/<path:filename>')
def serve_music(filename):
    # Décoder l'URL
    filename = unquote(filename)

    # Remplacer les backslashes par des forward slashes
    filename = filename.replace('\\', '/')

    # Construire le chemin sécurisé
    safe_path = safe_join(app.config['MUSIC_FOLDER'], filename)

    print(f"Tentative d'accès au fichier : {safe_path}")  # Log pour le débogage

    # Vérifier si le fichier existe
    if not os.path.isfile(safe_path):
        print(f"Fichier non trouvé: {safe_path}")  # Log pour le débogage
        abort(404, description="Fichier audio non trouvé")

    # Obtenir le répertoire et le nom de fichier
    directory = os.path.dirname(safe_path)
    file_name = os.path.basename(safe_path)

    try:
        return send_from_directory(directory, file_name)
    except Exception as e:
        print(f"Erreur lors de l'envoi du fichier: {str(e)}")  # Log pour le débogage
        abort(500, description="Erreur lors de l'envoi du fichier audio")


@app.route('/download_music_playlist_all/<string:playlist>')
def download_music_playlist_all(playlist):
    base_music_path = './musique'
    playlist_path = os.path.join(base_music_path, playlist)

    if not os.path.exists(playlist_path):
        flash(f"La playlist '{playlist}' n'existe pas.", "error")
        return redirect(url_for('listen_music'))

    # Récupérer tous les fichiers MP3 et miniatures dans le dossier de la playlist
    music_files = []
    for root, dirs, files in os.walk(playlist_path):
        for file in files:
            if file.endswith('.mp3'):
                relative_path = os.path.relpath(os.path.join(root, file), base_music_path)
                music_files.append(relative_path)

            # Vérifier si c'est une miniature et renommer si nécessaire
            elif file.lower().endswith(('.jpg', '.jpeg', '.png')):  # Extension typique d'image
                # Construire le chemin complet du fichier
                full_image_path = os.path.join(root, file)

                # Chemin de destination pour la renommer en "thumbnail.jpg"
                thumbnail_path = os.path.join(root, 'thumbnail.jpg')

                # Renommer le fichier s'il n'est pas déjà nommé "thumbnail.jpg"
                if not file.lower() == 'thumbnail.jpg':
                    os.rename(full_image_path, thumbnail_path)

    if not music_files:
        flash(f"Aucun fichier MP3 trouvé dans la playlist '{playlist}'.", "error")
        return redirect(url_for('listen_music'))

    return render_template('download_music_playlist_all.html', playlist=playlist, music_files=music_files)


@app.route('/download_file/<path:filename>')
def download_file(filename):
    # Décoder l'URL
    filename = unquote(filename)

    # Remplacer les backslashes par des forward slashes
    filename = filename.replace('\\', '/')

    # Définir le dossier des musiques
    music_folder = './musique'

    # Construire le chemin sécurisé
    safe_path = os.path.join(music_folder, filename)

    print(f"Tentative d'accès au fichier : {safe_path}")

    # Vérifier si le fichier existe
    if not os.path.isfile(safe_path):
        print(f"Fichier non trouvé: {safe_path}")
        abort(404, description="Fichier audio non trouvé")

    # Envoyer le fichier au client
    return send_file(safe_path, as_attachment=True)

    try:
        return send_from_directory(directory, file_name, as_attachment=True)
    except Exception as e:
        print(f"Erreur lors de l'envoi du fichier: {str(e)}")  # Log pour le débogage
        abort(500, description="Erreur lors du téléchargement du fichier audio")


def get_playlist_thumbnail(playlist_name):
    # Chemin du dossier de la playlist
    playlist_folder = os.path.join(app.config['MUSIC_FOLDER'], playlist_name)

    # Lister tous les fichiers dans le dossier
    if os.path.exists(playlist_folder):
        for file in os.listdir(playlist_folder):
            # Vérifier si le fichier commence par '0'
            if file.startswith('0') and (file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png')):
                return os.path.join(playlist_folder, file)

    # Retourne None si aucune miniature n'est trouvée
    return None


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=17000)