from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid
import traceback

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/info')
def get_info():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    ydl_opts = {'quiet': True, 'no_warnings': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        return jsonify({
            'title': info.get('title', 'YouTube Video'),
            'thumbnail': info.get('thumbnail'),
            'duration': info.get('duration_string', 'Unknown'),
            'views': f"{info.get('view_count', 0):,} views",
            'mp4_options': [
                {'name': '4K • 2160p', 'selector': 'bestvideo[height<=2160]+bestaudio/best', 'size': '~180 MB'},
                {'name': '1080p • Full HD', 'selector': 'bestvideo[height<=1080]+bestaudio/best', 'size': '~95 MB'},
                {'name': '720p • HD', 'selector': 'bestvideo[height<=720]+bestaudio/best', 'size': '~55 MB'},
                {'name': '480p', 'selector': 'bestvideo[height<=480]+bestaudio/best', 'size': '~28 MB'}
            ],
            'mp3_options': [
                {'name': '320kbps • Studio', 'selector': 'bestaudio/best', 'size': '~18 MB'},
                {'name': '256kbps • Premium', 'selector': 'bestaudio/best', 'size': '~14 MB'},
                {'name': '128kbps • Small', 'selector': 'bestaudio/best', 'size': '~8 MB'}
            ]
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/download')
def download_video():
    url = request.args.get('url')
    selector = request.args.get('selector')
    is_mp3 = request.args.get('mp3') == 'true'
    
    unique_id = uuid.uuid4().hex[:12]
    ydl_opts = {
        'format': selector,
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{unique_id}_%(title)s.%(ext)s'),
        'quiet': True,
        'concurrent_fragment_downloads': 8,
    }
    
    if is_mp3:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }]
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        # Force correct .mp3 extension
        if is_mp3 and not filename.lower().endswith('.mp3'):
            filename = os.path.splitext(filename)[0] + '.mp3'
        
        return jsonify({
            'success': True,
            'download_url': f'/api/serve?file={os.path.basename(filename)}'
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/serve')
def serve_file():
    file = request.args.get('file')
    path = os.path.join(DOWNLOAD_FOLDER, file)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return 'File not found', 404

if __name__ == '__main__':
    print("🚀 K Tube Downloader Backend (MP3 Fixed + Faster)")
    app.run(host='0.0.0.0', port=5000, debug=True)
