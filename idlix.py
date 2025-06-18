import requests
import json
from crypto_helper import CryptoJsAes, dec

class Idlix:
    BASE_WEB_URL = "https://id2.idlixvip.asia/"  # Ubah dengan URL dasar yang sesuai
    video_id = None
    video_type = "movie"  # Default adalah 'movie'
    embed_url = None
    embed_hash = None  # Tambahkan embed_hash untuk menyimpan ID dari embed_url

    def __init__(self, video_id, video_type="movie"):
        self.video_id = video_id
        self.video_type = video_type  # Menyimpan tipe video yang diterima

    def get_embed_url(self):
        if not self.video_id:
            return {
                'status': False,
                'message': 'Video ID is required'
            }
        try:
            # Mengirim permintaan POST dengan tipe video yang dinamis
            request = requests.post(
                url=self.BASE_WEB_URL + "wp-admin/admin-ajax.php",
                data={
                    "action": "doo_player_ajax",
                    "post": self.video_id,
                    "nume": "1",
                    "type": self.video_type,  # Gunakan tipe yang diterima
                }
            )

            if request.status_code == 200:
                try:
                    json_data = request.json()
                    embed_encrypted = json_data.get('embed_url')
                    key = json_data.get('key')

                    if embed_encrypted and key:
                        # Decrypt embed_url
                        decrypted_url = CryptoJsAes.decrypt(
                            embed_encrypted,
                            dec(embed_encrypted, json.loads(embed_encrypted).get('m'))
                        )
                        self.embed_url = decrypted_url
                        self.embed_hash = self.extract_hash_from_url(decrypted_url)

                        return {
                            'status': True,
                            'embed_url': self.embed_url,
                            'embed_hash': self.embed_hash,
                        }
                    else:
                        return {
                            'status': False,
                            'message': 'Embed URL or key missing in response',
                            'debug': json_data
                        }
                except Exception as parse_error:
                    return {
                        'status': False,
                        'message': f"Error parsing response or decrypting embed URL: {parse_error}",
                        'debug': request.text
                    }
            else:
                return {
                    'status': False,
                    'message': f"Request failed with status code {request.status_code}",
                    'debug': request.text
                }
        except Exception as error_get_embed_url:
            return {
                'status': False,
                'message': f"Exception occurred: {str(error_get_embed_url)}"
            }

    @staticmethod
    def extract_hash_from_url(url):
        """Ekstrak hash ID dari embed_url."""
        try:
            return url.split("/")[-1]
        except Exception as e:
            return None
