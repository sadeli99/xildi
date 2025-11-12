import requests
import json
from crypto_helper import CryptoJsAes, dec

class Idlix:
    BASE_WEB_URL = "https://tv10.idlixku.com/"  # Ubah dengan URL dasar yang sesuai
    video_id = None
    embed_url = None

    def __init__(self, video_id):
        self.video_id = video_id

    def get_embed_url(self):
        if not self.video_id:
            return {
                'status': False,
                'message': 'Video ID is required'
            }
        try:
            request = requests.post(
                url=self.BASE_WEB_URL + "wp-admin/admin-ajax.php",
                data={
                    "action": "doo_player_ajax",
                    "post": self.video_id,
                    "nume": "1",
                    "type": "movie",
                }
            )
            if request.status_code == 200 and request.json().get('embed_url'):
                self.embed_url = CryptoJsAes.decrypt(
                    request.json().get('embed_url'),
                    dec(
                        request.json().get('key'),
                        json.loads(request.json().get('embed_url')).get('m')
                    )
                )
                return {
                    'status': True,
                    'embed_url': self.embed_url
                }
            else:
                return {
                    'status': False,
                    'message': 'Failed to get embed URL'
                }
        except Exception as error_get_embed_url:
            return {
                'status': False,
                'message': str(error_get_embed_url)
            }
