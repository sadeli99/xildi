import json
from crypto_helper import CryptoJsAes, dec

class Idlix:
    embed_url = None
    embed_hash = None

    def __init__(self, embed_data: dict):
        """
        embed_data = dict Python yang sudah di-parse dari request JSON Flask
        Harus mengandung 'embed_url' (string JSON terenkripsi) dan 'key'
        """
        self.embed_encrypted = embed_data.get("embed_url")
        self.key = embed_data.get("key")

    def process_embed(self):
    if not self.embed_encrypted or not self.key:
        return {
            "status": False,
            "message": "Embed URL atau key tidak ditemukan"
        }

    try:
        # embed_url adalah JSON terenkripsi → parse
        embed_json = json.loads(self.embed_encrypted)

        # Decode key dari format \xNN ke string biasa
        decoded_key = self.key.encode('utf-8').decode('unicode_escape')

        # Dekripsi URL
        decrypted_url = CryptoJsAes.decrypt(
            self.embed_encrypted,
            decoded_key
        )

        self.embed_url = decrypted_url
        self.embed_hash = self.extract_hash_from_url(decrypted_url)

        return {
            "status": True,
            "embed_url": self.embed_url,
            "embed_hash": self.embed_hash
        }
    except Exception as e:
        return {
            "status": False,
            "message": f"Gagal dekripsi: {e}"
        }

    @staticmethod
    def extract_hash_from_url(url):
        try:
            return url.split("/")[-1]
        except Exception:
            return None
