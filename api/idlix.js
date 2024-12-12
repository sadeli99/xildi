const { dec } = require('./CryptoJsAes');
const fetch = require('node-fetch');
const CryptoJsAes = require('./CryptoJsAes');

class Idlix {
    constructor(videoId) {
        this.BASE_WEB_URL = 'https://tv4.idlix.asia/';
        this.video_id = videoId;
        this.embed_url = null;
    }

    async getEmbedUrl() {
        if (!this.video_id) {
            return {
                status: false,
                message: 'Video ID is required'
            };
        }

        try {
            const response = await fetch(`${this.BASE_WEB_URL}wp-admin/admin-ajax.php`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({
                    action: 'doo_player_ajax',
                    post: this.video_id,
                    nume: '1',
                    type: 'movie'
                })
            });

            const jsonResponse = await response.json();

            if (response.status === 200 && jsonResponse.embed_url) {
                this.embed_url = CryptoJsAes.decrypt(
                    jsonResponse.embed_url,
                    dec(jsonResponse.key, JSON.parse(jsonResponse.embed_url).m)
                );

                return {
                    status: true,
                    embed_url: this.embed_url
                };
            } else {
                return {
                    status: false,
                    message: 'Failed to get embed URL'
                };
            }
        } catch (error) {
            return {
                status: false,
                message: error.toString()
            };
        }
    }
}

// Fungsi utama untuk menjalankan logika
(async () => {
    const videoId = '124474'; // ID Video yang diinginkan

    const idlix = new Idlix(videoId);
    const result = await idlix.getEmbedUrl();
    console.log(result); // Hasil embed URL atau error
})();
