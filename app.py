from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
import uuid

app = Flask(__name__)

# Store progress globally (can also use Redis/DB if scaling)
progress_data = {"percent": 0, "status": "idle"}


def progress_hook(d):
    """Capture yt_dlp progress"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '').strip()
        if percent.endswith('%'):
            try:
                progress_data["percent"] = int(float(percent.replace('%', '')))
                progress_data["status"] = "downloading"
            except:
                pass
    elif d['status'] == 'finished':
        progress_data["percent"] = 100
        progress_data["status"] = "finished"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        try:
            filename = f"{uuid.uuid4()}.mp4"
            filepath = os.path.join("temp", filename)
            os.makedirs("temp", exist_ok=True)

            ydl_opts = {
                "format": "best",
                "outtmpl": filepath,
                "progress_hooks": [progress_hook],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return send_file(filepath, as_attachment=True)

        except Exception as e:
            return f"❌ Error: {str(e)}"

    return render_template("index.html")


@app.route("/progress")
def progress():
    """Return current progress as JSON"""
    return jsonify(progress_data)


if __name__ == "__main__":
    app.run(debug=True)
