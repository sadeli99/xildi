from flask import Flask, request, jsonify
from idlix import Idlix

app = Flask(__name__)

@app.route('/get_embed_url', methods=['POST'])
def get_embed_url():
    data = request.json
    video_id = data.get('video_id')

    if not video_id:
        return jsonify({"error": "Missing 'video_id'"}), 400

    idlix_instance = Idlix(video_id)
    result = idlix_instance.get_embed_url()

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
