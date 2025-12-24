from flask import Flask, render_template, request, jsonify, send_file, session
import yt_dlp
import os
import uuid
from threading import Thread

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET"

PASSWORD = "1234"  # 🔐 change this password
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

progress_data = {}
file_data = {}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return render_template("index.html")
        return render_template("login.html", error="Wrong password")
    return render_template("login.html")

@app.route("/download", methods=["POST"])
def download():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    url = request.form["url"]
    quality = request.form["quality"]
    task_id = str(uuid.uuid4())

    Thread(target=start_download, args=(task_id, url, quality)).start()
    return jsonify({"task_id": task_id})

def start_download(task_id, url, quality):
    def hook(d):
        if d["status"] == "downloading":
            progress_data[task_id] = d.get("_percent_str", "0%")
        elif d["status"] == "finished":
            progress_data[task_id] = "100%"

    ydl_opts = {
        "format": f"bestvideo[height<={quality}]+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
        "progress_hooks": [hook],
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".mp4").replace(".mkv", ".mp4")
        file_data[task_id] = filename

@app.route("/progress/<task_id>")
def progress(task_id):
    return jsonify({"progress": progress_data.get(task_id, "0%")})

@app.route("/file/<task_id>")
def get_file(task_id):
    filepath = file_data.get(task_id)
    if filepath and os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return "File not ready", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
