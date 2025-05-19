# Trigger redeploy da Giorgio
from flask import Flask, request, send_file, render_template, redirect, url_for, flash, session, send_from_directory
import yt_dlp
import os
import uuid
import json
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Cambiala se vuoi
USERNAME = "GTSHFJNVHDI18.9OCJ"
PASSWORD = "JJHDFSJQ9374JFMVHXI,UYGHKLO987Y!!!!"
app.secret_key = "supersecretkey"  # Cambiala se vuoi
DOWNLOAD_FOLDER = "musica_offline"
PLAYLIST_FILE = "playlists.json"

def load_playlists():
    if not os.path.exists(PLAYLIST_FILE):
        return {}
    with open(PLAYLIST_FILE, "r") as f:
        return json.load(f)

def save_playlists(data):
    with open(PLAYLIST_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route('/music/<filename>')
def serve_music(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename))

@app.route("/")
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)   
    files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith('.mp3')]
    playlists = load_playlists()
    return render_template("index.html", files=files, playlists=playlists)

@app.route("/download", methods=["POST"])
def download():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    url = request.form.get("url")
    if not url:
        flash("URL mancante", "error")
        return redirect(url_for('index'))

    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    file_id = str(uuid.uuid4())
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOAD_FOLDER}/{file_id}.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    flash("Download completato!", "success")
    return redirect(url_for('index'))

@app.route("/rename", methods=["POST"])
def rename_file():
    old_name = request.form.get("old_name")
    new_name = request.form.get("new_name")
    if not old_name or not new_name:
        flash("Nome file vecchio o nuovo mancante", "error")
        return redirect(url_for('index'))

    if not new_name.endswith(".mp3"):
        new_name += ".mp3"

    old_path = os.path.join(DOWNLOAD_FOLDER, old_name)
    new_path = os.path.join(DOWNLOAD_FOLDER, new_name)

    if os.path.exists(new_path):
        flash("Un file con questo nome esiste già!", "error")
        return redirect(url_for('index'))

    try:
        os.rename(old_path, new_path)
        flash(f"File rinominato in {new_name}", "success")
    except Exception as e:
        flash(f"Errore durante la rinomina: {str(e)}", "error")

    return redirect(url_for('index'))

@app.route("/playlist/create", methods=["POST"])
def create_playlist():
    playlists = load_playlists()
    name = request.form.get("playlist_name")
    if not name:
        flash("Nome playlist mancante", "error")
        return redirect(url_for('index'))

    if name in playlists:
        flash("Playlist già esistente", "error")
        return redirect(url_for('index'))

    playlists[name] = []
    save_playlists(playlists)
    flash(f"Playlist '{name}' creata", "success")
    return redirect(url_for('index'))

@app.route("/playlist/add", methods=["POST"])
def add_to_playlist():
    playlists = load_playlists()
    playlist_name = request.form.get("playlist_name")
    file_name = request.form.get("file_name")
    if not playlist_name or not file_name:
        flash("Playlist o file non specificato", "error")
        return redirect(url_for('index'))

    if playlist_name not in playlists:
        flash("Playlist non trovata", "error")
        return redirect(url_for('index'))

    if file_name not in playlists[playlist_name]:
        playlists[playlist_name].append(file_name)
        save_playlists(playlists)
        flash(f"Aggiunto {file_name} a {playlist_name}", "success")
    else:
        flash("File già presente in playlist", "warning")

    return redirect(url_for('index'))

@app.route("/playlist/<name>")
def show_playlist(name):
if not session.get('logged_in'):
    return redirect(url_for('login'))
    playlists = load_playlists()
    if name not in playlists:
        flash("Playlist non trovata", "error")
        return redirect(url_for('index'))

    files = playlists[name]
    return render_template("playlist.html", playlist_name=name, files=files)

@app.route("/playlist/play/<name>")
def play_playlist(name):
    playlists = load_playlists()
    if name not in playlists:
        flash("Playlist non trovata", "error")
        return redirect(url_for('index'))

    files = playlists[name]
    return render_template("play_playlist.html", playlist_name=name, files=files)
from flask import send_from_directory

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Credenziali errate', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')
if __name__ == "__main__":
    import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
