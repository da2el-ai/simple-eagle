import requests
import json
import os
from urllib.parse import unquote
from .util import load_image


# デバッグモード（環境変数で制御）
DEBUG = os.getenv('EAGLE_DEBUG', 'false').lower() == 'true'
DEBUG_LIMIT = 5
MAX_FILE_SIZE = 768
QUALITY = 85

class EagleApi:
    def __init__(self):
        self.base_url = 'http://localhost:41595'

    def get_recent_images(self, limit=100):
        """
        最新の画像一覧を取得
        """
        try:
            print(f"Requesting recent images from Eagle API with limit: {limit}")
            response = requests.get(f'{self.base_url}/api/item/list?limit={limit}')
            response.raise_for_status()
            data = response.json()
            print(f"Eagle API response received. Status: {response.status_code}")

            if 'data' in data and isinstance(data['data'], list):
                if DEBUG:
                    print(f"DEBUG MODE: Limiting results to {DEBUG_LIMIT} items")
                    data['data'] = data['data'][:DEBUG_LIMIT]
                print(f"Processing {len(data['data'])} items")
            else:
                print("Unexpected data structure:", data)

            return data
        except requests.exceptions.RequestException as e:
            error_msg = f"Eagle API error: {str(e)}"
            print(error_msg)
            if hasattr(response, 'text'):
                print(f"Response content: {response.text}")
            return {"status": "error", "message": error_msg}

    def get_folder_list(self):
        """フォルダ一覧を取得"""
        try:
            response = requests.get(f'{self.base_url}/api/folder/list')
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Eagle API error: {e}")
            return {"status": "error", "message": str(e)}

    def get_thumbnail_image(self, image_id):
        """
        指定したIDのサムネイル画像を取得して Base64で返す
        """
        try:
            response = requests.get(f"{self.base_url}/api/item/thumbnail?id={image_id}")
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'success' and 'data' in data:
                # URLエンコードされたパスをデコード
                decoded_path = unquote(data['data'])
                # ローカルファイルパスから画像を読み込む
                return load_image(decoded_path)
            else:
                print(f"Unexpected response: {data}")
                return None
                
        except (requests.exceptions.RequestException, IOError) as e:
            print(f"Error getting thumbnail image: {e}")
            return None

    def get_image(self, image_id, ext="png", max_file_size=MAX_FILE_SIZE, quality=QUALITY):
        """
        - 指定したIDのオリジナル画像を返す
        - サムネイルはオリジナルと同じフォルダにあり、`{ファイル名}_thumbnail.png` という名前なので、そこからオリジナルを取得する
        - サムネイルファイル名に `_thumbnail.png` が無ければオリジナルがサムネイルとして使われている
        - 拡張子は引数 ext を使う
        """
        try:
            response = requests.get(f"{self.base_url}/api/item/thumbnail?id={image_id}")
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'success' and 'data' in data:
                path = unquote(data['data'])
                if path.endswith('_thumbnail.png'):
                    # サムネイルの場合、オリジナルのパスを生成
                    # '_thumbnail.png' を削除してオリジナルの拡張子に変更
                    base_path = path[:-14]  # '_thumbnail.png' の長さ(14)を削除
                    original_path = f"{base_path}.{ext}"
                else:
                    # サムネイルが作られていない場合は、パスをそのまま使用
                    original_path = path
                # ローカルファイルパスから画像を読み込む
                return load_image(original_path, max_file_size, quality)
            else:
                print(f"Unexpected response: {data}")
                return None
                
        except (requests.exceptions.RequestException, IOError) as e:
            print(f"Error getting image: {e}")
            return None


    def get_image_info(self, image_id):
        """
        画像の詳細情報を取得
        しかし /item/list で取得できるものとほぼ同じ（？）なので今回は使わないのでは？
        """
        try:
            response = requests.get(f'{self.base_url}/api/item/info?id={image_id}')
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting image detail: {e}")
            return None

eagle_api = EagleApi()
