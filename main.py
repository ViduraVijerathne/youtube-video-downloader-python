from flask import Flask, jsonify, request
from yt_dlp import YoutubeDL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Helper function to get video info and progressive MP4 formats
def get_video_info(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = []
        for f in info['formats']:
            # Filter for progressive MP4 formats (not HLS or adaptive)
            if (f.get('vcodec') != 'none' and
                    f.get('acodec') != 'none' and
                    f.get('ext') == 'mp4' and
                    'height' in f and
                    'url' in f):
                quality = f"{f['height']}p"
                formats.append({
                    'quality': quality,
                    'url': f['url']
                })
        return formats

# Existing endpoint to get a direct download link for a specific quality
@app.route('/download-link', methods=['GET'])
def download_link():
    video_id = request.args.get('videoID')
    quality = request.args.get('quality')

    # Validate input
    if not video_id or not quality:
        return jsonify({"error": "videoID and quality are required"}), 400

    try:
        # Fetch available MP4 formats
        formats = get_video_info(video_id)
        selected_format = None
        for f in formats:
            if f['quality'] == quality:
                selected_format = f
                break
        if not selected_format:
            return jsonify({"error": f"Quality {quality} not available as a direct download"}), 404

        # Return the direct MP4 URL
        return jsonify({"download_link": selected_format['url']})
    except Exception as e:
        return jsonify({"error": "An error occurred"}), 500

# New endpoint to get direct download links for all available formats
@app.route('/all-format-download-links', methods=['GET'])
def all_format_download_links():
    video_id = request.args.get('videoID')

    # Validate input
    if not video_id:
        return jsonify({"error": "videoID is required"}), 400

    try:
        # Fetch available MP4 formats
        formats = get_video_info(video_id)
        # Transform the list to match the required format
        result = [{"format": f['quality'], "url": f['url']} for f in formats]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching formats"}), 500

@app.route('/all-format-download-links2', methods=['GET'])
def all_format_download_links2():
    video_id = request.args.get('videoID')
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return jsonify(info)




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)