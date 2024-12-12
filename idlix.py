import requests
from urllib.parse import urlparse
import json
import base64
from cryptojs_aes import CryptoJsAes  # Mengimpor kelas CryptoJsAes untuk dekripsi URL yang dienkripsi

class Idlix:
    BASE_WEB_URL = 'https://tv4.idlix.asia/'  # URL dasar dari situs

    def __init__(self, video_id):
        self.video_id = video_id  # Menyimpan ID video yang diberikan
        self.embed_url = None  # Inisialisasi variabel embed_url yang nantinya akan berisi URL embed
        self.m3u8_url = None  # Inisialisasi variabel m3u8_url yang nantinya akan berisi URL m3u8

    def get_embed_url(self):
        """
        Mendapatkan embed URL menggunakan video_id yang diberikan.
        Setelah mendapatkan embed URL, dekripsi dilakukan menggunakan CryptoJsAes
        dan hasilnya disimpan dalam self.embed_url.
        """
        if not self.video_id:  # Mengecek apakah video_id ada
            return {
                'status': False,
                'message': 'Video ID is required'  # Jika tidak ada video_id, mengembalikan pesan kesalahan
            }

        try:
            # Mengirim POST request ke URL untuk mendapatkan embed_url
            request = requests.post(
                url=self.BASE_WEB_URL + "wp-admin/admin-ajax.php",
                data={
                    "action": "doo_player_ajax",
                    "post": self.video_id,  # Mengirim video_id sebagai data
                    "nume": "1",  # Parameter lainnya yang diperlukan untuk request
                    "type": "movie",  # Tipe konten yang diminta (film)
                }
            )

            # Jika request berhasil dan mendapatkan embed_url, lanjutkan proses dekripsi
            if request.status_code == 200 and request.json().get('embed_url'):
                self.embed_url = CryptoJsAes.decrypt(
                    request.json().get('embed_url'),  # Mendekripsi embed_url
                    self._dec(  # Proses dekripsi lainnya dengan key yang diperlukan
                        request.json().get('key'),
                        json.loads(request.json().get('embed_url')).get('m')
                    )
                )
                return {
                    'status': True,
                    'embed_url': self.embed_url  # Mengembalikan embed_url jika berhasil
                }
            else:
                return {
                    'status': False,
                    'message': 'Failed to get embed URL'  # Jika tidak berhasil, mengembalikan pesan kesalahan
                }
        except Exception as error_get_embed_url:
            # Menangani kesalahan jika terjadi kesalahan dalam permintaan atau dekripsi
            return {
                'status': False,
                'message': str(error_get_embed_url)  # Mengembalikan pesan kesalahan
            }

    def get_m3u8_url(self):
        """
        Setelah embed_url berhasil diperoleh, fungsi ini akan mencari dan mendapatkan m3u8 URL.
        Ini memungkinkan untuk streaming video dengan m3u8.
        """
        if not self.embed_url:  # Mengecek apakah embed_url ada
            return {
                'status': False,
                'message': 'Embed URL is required'  # Jika tidak ada embed_url, mengembalikan pesan kesalahan
            }

        # Memproses embed_url untuk mendapatkan video ID atau hash yang diperlukan
        if '/video/' in urlparse(self.embed_url).path:
            self.embed_url = urlparse(self.embed_url).path.split('/')[2]  # Mengambil bagian dari URL
        elif urlparse(self.embed_url).query.split('=')[1]:
            self.embed_url = urlparse(self.embed_url).query.split('=')[1]

        try:
            # Mengirim POST request untuk mendapatkan m3u8 URL
            request = requests.post(
                url='https://jeniusplay.com/player/index.php',
                params={
                    "data": self.embed_url,  # Menyertakan embed_url dalam parameter data
                    "do": "getVideo"  # Tindakan yang diminta adalah untuk mendapatkan video
                },
                headers={
                    "Host": "jeniusplay.com",  # Header yang diperlukan untuk permintaan
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                },
                data={
                    "hash": self.embed_url,  # Menyertakan hash yang diperlukan
                    "r": self.BASE_WEB_URL,  # URL sumber yang digunakan
                },
            )

            # Jika request berhasil dan terdapat 'videoSource', berarti m3u8 URL ditemukan
            if request.status_code == 200 and request.json().get('videoSource'):
                self.m3u8_url = request.json().get('videoSource')  # Menyimpan m3u8 URL
                return {
                    'status': True,
                    'm3u8_url': self.m3u8_url  # Mengembalikan m3u8 URL jika berhasil
                }
            else:
                return {
                    'status': False,
                    'message': 'Failed to get m3u8 URL'  # Jika gagal, mengembalikan pesan kesalahan
                }
        except Exception as error_get_m3u8_url:
            # Menangani kesalahan jika terjadi kesalahan dalam permintaan untuk mendapatkan m3u8 URL
            return {
                'status': False,
                'message': str(error_get_m3u8_url)  # Mengembalikan pesan kesalahan
            }

    def _dec(self, r, e):
        """
        Fungsi ini digunakan untuk mendekripsi data yang diberikan dengan key dan data yang sesuai.
        Ini digunakan untuk memproses data yang diberikan oleh server.
        """
        r_list = [r[i:i + 2] for i in range(2, len(r), 4)]  # Membagi data key menjadi bagian-bagian
        m_padded = self._add_base64_padding(e[::-1])  # Memproses data enkripsi dan menambahkan padding base64
        try:
            decoded_m = base64.b64decode(m_padded).decode('utf-8')  # Mendekodekan data base64 yang sudah diproses
        except base64.binascii.Error as e:
            print(f"Base64 decoding error: {e}")  # Menangani kesalahan decoding
            return ""

        decoded_m_list = decoded_m.split("|")  # Memisahkan hasil decode berdasarkan '|'
        # Menggabungkan hasilnya menjadi string dengan format \x untuk setiap karakter
        return "".join("\\x" + r_list[int(s)] for s in decoded_m_list if s.isdigit() and int(s) < len(r_list))

    @staticmethod
    def _add_base64_padding(b64_string):
        """
        Menambahkan padding pada string base64 agar panjangnya sesuai.
        """
        return b64_string + '=' * (-len(b64_string) % 4)  # Menambahkan padding '=' jika perlu
