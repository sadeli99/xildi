from flask import Flask, request, jsonify
from idlix import Idlix

app = Flask(__name__)

@app.route('/get_embed_url', methods=['POST'])
def get_embed_url():
    # Mengambil data JSON dari body request
    data = request.json
    video_id = data.get('video_id')
    video_type = data.get('video_type', 'movie')  # Default 'movie' jika tidak ada

    # Memastikan video_id ada
    if not video_id:
        return jsonify({"error": "Missing 'video_id'"}), 400

    # Membuat instance Idlix dengan video_id dan video_type
    idlix_instance = Idlix(video_id, video_type)
    result = idlix_instance.get_embed_url()

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
