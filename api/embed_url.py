from api.idlixhelper import IdlixHelper
import json

def handler(request):
    # Mendapatkan parameter video_id dari URL atau body request
    video_id = request.args.get('video_id')  # atau request.json['video_id'] untuk POST

    if not video_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'status': False, 'message': 'Video ID is required'})
        }

    # Membuat instance dan memanggil metode get_embed_url
    idlix_helper = IdlixHelper(video_id)
    response = idlix_helper.get_embed_url()

    # Mengembalikan response dalam format JSON
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
