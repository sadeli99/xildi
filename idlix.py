import requests
import json
from crypto_helper import CryptoJsAes, dec
from urllib.parse import urlparse

class Idlix:
    BASE_WEB_URL = "https://tv4.idlix.asia/"  # URL dasar untuk API yang digunakan
    def __init__(self, video_id):
        self.video_id = video_id
        self.embed_url = None
        self.m3u8_url = None

    def get_embed_url(self):
        """
        Fungsi ini untuk mendapatkan embed URL dari IDLIX dengan menggunakan video_id yang diberikan.
        """
        if not self.video_id:
            return {
                'status': False,
                'message': 'Video ID is required'
            }

        try:
            # Mengirim permintaan POST ke server IDLIX untuk mendapatkan embed URL
            request = requests.post(
                url=self.BASE_WEB_URL + "wp-admin/admin-ajax.php",
                data={
                    "action": "doo_player_ajax",
                    "post": self.video_id,
                    "nume": "1",
                    "type": "movie",
                }
            )
            
            # Mengecek apakah request berhasil dan ada embed_url dalam respons
            if request.status_code == 200 and request.json().get('embed_url'):
                # Mendekripsi embed_url menggunakan CryptoJsAes dan key yang diberikan
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

    def get_m3u8_url(self):
        """
        Fungsi ini untuk mendapatkan URL video dalam format M3U8 berdasarkan embed_url yang telah diperoleh.
        """
        if not self.embed_url:
            return {
                'status': False,
                'message': 'Embed URL is required'
            }

        # Mengambil bagian tertentu dari embed_url (seperti ID video atau path)
        if '/video/' in urlparse(self.embed_url).path:
            self.embed_url = urlparse(self.embed_url).path.split('/')[2]
        elif urlparse(self.embed_url).query.split('=')[1]:
            self.embed_url = urlparse(self.embed_url).query.split('=')[1]

        try:
            # Mengirim permintaan POST untuk mendapatkan M3U8 URL berdasarkan embed_url
            request = requests.post(
                url='https://jeniusplay.com/player/index.php',
                params={
                    "data": self.embed_url,
                    "do": "getVideo"
                },
                headers={
                    "Host": "jeniusplay.com",
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                },
                data={
                    "hash": self.embed_url,
                    "r": self.BASE_WEB_URL,
                },
            )

            # Mengecek apakah permintaan berhasil dan ada videoSource (M3U8 URL)
            if request.status_code == 200 and request.json().get('videoSource'):
                self.m3u8_url = request.json().get('videoSource')
                return {
                    'status': True,
                    'm3u8_url': self.m3u8_url
                }
            else:
                return {
                    'status': False,
                    'message': 'Failed to get M3U8 URL'
                }

        except Exception as error_get_m3u8_url:
            return {
                'status': False,
                'message': str(error_get_m3u8_url)
            }
