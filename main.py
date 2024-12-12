from flask import Flask, request, jsonify
from idlix import Idlix

app = Flask(__name__)

@app.route('/get_embed_url', methods=['POST'])
def get_embed_url():
    data = request.json
    video_id = data.get('video_id')

    if not video_id:
        return jsonify({"error": "Missing 'video_id'"}), 400

    # Membuat instance dari kelas Idlix dengan video_id yang diberikan
    idlix_instance = Idlix(video_id)
    
    # Memanggil fungsi untuk mendapatkan embed_url
    embed_url_result = idlix_instance.get_embed_url()

    # Jika embed_url berhasil didapatkan, lanjutkan untuk mendapatkan m3u8 URL
    if embed_url_result['status']:
        # Setelah embed_url berhasil didapatkan, panggil get_m3u8_url untuk mendapatkan m3u8 URL
        m3u8_url_result = idlix_instance.get_m3u8_url()
        # Gabungkan hasil embed_url dan m3u8_url dalam satu respon
        if m3u8_url_result['status']:
            return jsonify({
                'status': True,
                'embed_url': embed_url_result['embed_url'],
                'm3u8_url': m3u8_url_result['m3u8_url']
            })
        else:
            return jsonify(m3u8_url_result)  # Mengembalikan error dari get_m3u8_url jika gagal
    else:
        return jsonify(embed_url_result)  # Mengembalikan error dari get_embed_url jika gagal

if __name__ == '__main__':
    app.run(debug=True)
