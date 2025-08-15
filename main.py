from flask import Flask, request, jsonify
from idlix import Idlix

app = Flask(__name__)

@app.route('/get_embed_url', methods=['POST'])
def get_embed_url():
    data = request.json  # ini sudah dict
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    idlix_instance = Idlix(data)
    result = idlix_instance.process_embed()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
