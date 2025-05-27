import base64
import os
import hashlib
import time
from datetime import datetime, timedelta
from PIL import Image, ImageFile
import io
from .debug_logger import debug_print

# PILの画像サイズ制限を緩和（decompression bomb対策を無効化）
Image.MAX_IMAGE_PIXELS = None
ImageFile.LOAD_TRUNCATED_IMAGES = True

# キャッシュディレクトリ
CACHE_DIR = "cache"
CACHE_EXPIRY_HOURS = 1

def get_cache_key(path: str, max_file_size: int, quality: int) -> str:
    """キャッシュキーを生成"""
    # ファイルパス、最終更新時刻、パラメータからハッシュを生成
    try:
        mtime = os.path.getmtime(path)
        key_string = f"{path}_{mtime}_{max_file_size}_{quality}"
        return hashlib.md5(key_string.encode()).hexdigest()
    except OSError:
        # ファイルが存在しない場合
        return None

def get_cache_path(cache_key: str) -> str:
    """キャッシュファイルのパスを取得"""
    return os.path.join(CACHE_DIR, f"{cache_key}.cache")

def is_cache_valid(cache_path: str) -> bool:
    """キャッシュが有効かどうかチェック（1時間以内）"""
    if not os.path.exists(cache_path):
        return False
    
    try:
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        expiry_time = datetime.now() - timedelta(hours=CACHE_EXPIRY_HOURS)
        return cache_time > expiry_time
    except OSError:
        return False

def load_from_cache(cache_path: str):
    """キャッシュからデータを読み込み"""
    try:
        with open(cache_path, 'rb') as f:
            # 最初の4バイトでContent-Typeの長さを読み取り
            content_type_length = int.from_bytes(f.read(4), byteorder='big')
            # Content-Typeを読み取り
            content_type = f.read(content_type_length).decode('utf-8')
            # 残りが画像データ
            content = f.read()
            return content, content_type
    except Exception as e:
        debug_print(f"Error loading from cache {cache_path}: {e}")
        return None

def save_to_cache(cache_path: str, content: bytes, content_type: str):
    """データをキャッシュに保存"""
    try:
        # キャッシュディレクトリを作成
        os.makedirs(CACHE_DIR, exist_ok=True)
        
        with open(cache_path, 'wb') as f:
            # Content-Typeの長さを4バイトで書き込み
            content_type_bytes = content_type.encode('utf-8')
            f.write(len(content_type_bytes).to_bytes(4, byteorder='big'))
            # Content-Typeを書き込み
            f.write(content_type_bytes)
            # 画像データを書き込み
            f.write(content)
        
        debug_print(f"Saved to cache: {cache_path}")
    except Exception as e:
        debug_print(f"Error saving to cache {cache_path}: {e}")

def cleanup_expired_cache():
    """期限切れのキャッシュファイルを削除"""
    if not os.path.exists(CACHE_DIR):
        return
    
    try:
        expiry_time = datetime.now() - timedelta(hours=CACHE_EXPIRY_HOURS)
        deleted_count = 0
        
        for filename in os.listdir(CACHE_DIR):
            if filename.endswith('.cache'):
                cache_path = os.path.join(CACHE_DIR, filename)
                try:
                    cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
                    if cache_time <= expiry_time:
                        os.remove(cache_path)
                        deleted_count += 1
                except OSError:
                    # ファイルが削除できない場合はスキップ
                    pass
        
        if deleted_count > 0:
            debug_print(f"Cleaned up {deleted_count} expired cache files")
    except Exception as e:
        debug_print(f"Error during cache cleanup: {e}")

# def detect_image_type(data: bytes) -> str:
#     """
#     画像データの内容からMIMEタイプを判断
#     """
#     if data.startswith(b'RIFF') and b'WEBP' in data[0:12]:
#         return 'image/webp'
#     elif data.startswith(b'\x89PNG\r\n\x1a\n'):
#         return 'image/png'
#     elif data.startswith(b'\xff\xd8\xff'):
#         return 'image/jpeg'
#     elif data.startswith(b'GIF87a') or data.startswith(b'GIF89a'):
#         return 'image/gif'
#     return None

def load_image(path: str, max_file_size=0, quality=85):
    """
    ローカルファイルパスから画像を読み込む（キャッシュ機能付き）
    - path: 画像パス
    - max_file_size: ファイルサイズがこの値より大きかったらjpeg圧縮をかける。0なら圧縮しない（KB単位）
    - quality: jpeg圧縮率
    - 戻り値: (バイナリデータ, Content-Type)のタプル
    """
    try:
        # 期限切れキャッシュのクリーンアップ（たまに実行）
        import random
        if random.randint(1, 100) == 1:  # 1%の確率で実行
            cleanup_expired_cache()
        
        # ファイルサイズを事前にチェック
        file_size = os.path.getsize(path)
        file_size_kb = file_size / 1024
        
        debug_print(f"Loading image: {path}, size: {file_size_kb:.2f}KB")
        
        # 非常に大きいファイル（50MB以上）は処理を拒否
        if file_size > 50 * 1024 * 1024:  # 50MB
            raise ValueError(f"Image file too large: {file_size_kb:.2f}KB (max 50MB)")
        
        # 圧縮が必要な場合のみキャッシュを使用
        should_compress = max_file_size > 0 and file_size_kb > max_file_size
        cache_key = None
        cache_path = None
        
        if should_compress:
            # キャッシュキーを生成
            cache_key = get_cache_key(path, max_file_size, quality)
            if cache_key is None:
                raise FileNotFoundError(f"Image file not found: {path}")
            
            cache_path = get_cache_path(cache_key)
            
            # キャッシュが有効な場合はキャッシュから読み込み
            if is_cache_valid(cache_path):
                cached_data = load_from_cache(cache_path)
                if cached_data is not None:
                    debug_print(f"Loaded from cache: {cache_path}")
                    return cached_data
        
        # max_file_sizeが0でない場合、かつファイルサイズが制限を超える場合は圧縮
        if max_file_size > 0 and file_size_kb > max_file_size:
            debug_print(f"Compressing image from {file_size_kb:.2f}KB to target {max_file_size}KB")
            
            try:
                # PILで画像を開く
                with Image.open(path) as image:
                    debug_print(f"Original image size: {image.size} ({image.size[0] * image.size[1]} pixels)")
                    
                    # 画像サイズが非常に大きい場合はリサイズ
                    # ファイルサイズに応じて最大解像度を調整
                    if file_size_kb > 10000:  # 10MB以上
                        max_dimension = 2048  # 2K解像度
                    elif file_size_kb > 5000:  # 5MB以上
                        max_dimension = 3072  # 3K解像度
                    else:
                        max_dimension = 4096  # 4K解像度
                    
                    if max(image.size) > max_dimension:
                        ratio = max_dimension / max(image.size)
                        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                        image = image.resize(new_size, Image.Resampling.LANCZOS)
                        debug_print(f"Resized image to {new_size} ({new_size[0] * new_size[1]} pixels)")
                    
                    # RGBAモードの場合はRGBに変換（JPEG保存のため）
                    if image.mode in ('RGBA', 'LA', 'P'):
                        # 透明度がある場合は白背景で合成
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        if image.mode == 'P':
                            image = image.convert('RGBA')
                        background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                        image = background
                    elif image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # メモリ上でJPEG圧縮
                    output = io.BytesIO()
                    image.save(output, format='JPEG', quality=quality, optimize=True)
                    content = output.getvalue()
                    content_type = 'image/jpeg'
                    
                    compressed_size_kb = len(content) / 1024
                    debug_print(f"Compressed to {compressed_size_kb:.2f}KB")
                    
            except Exception as compression_error:
                debug_print(f"Compression failed: {compression_error}, falling back to original")
                # 圧縮に失敗した場合は元ファイルを返す
                with open(path, 'rb') as image_file:
                    content = image_file.read()
                content_type = get_content_type_from_path(path)
        else:
            # 圧縮しない場合は元のファイルを読み込み
            with open(path, 'rb') as image_file:
                content = image_file.read()
            content_type = get_content_type_from_path(path)
        
        # 圧縮が実行された場合のみキャッシュに保存
        if should_compress and cache_path is not None:
            save_to_cache(cache_path, content, content_type)
        
        return content, content_type
        
    except Exception as e:
        debug_print(f"Error loading image {path}: {e}")
        raise

def get_content_type_from_path(path: str) -> str:
    """ファイルパスからContent-Typeを取得"""
    return 'image/webp' if path.endswith('.webp') \
          else 'image/png' if path.endswith('.png') \
          else 'image/jpeg' if path.endswith(('.jpg', '.jpeg')) \
          else 'image/gif' if path.endswith('.gif') \
          else 'application/octet-stream'

# def filepath_to_base64(path:str):
#     """
#     ローカルファイルパスから画像を読み込み Base64で返す
#     """
#     mime_types = {
#         '.png': 'image/png',
#         '.jpg': 'image/jpeg',
#         '.jpeg': 'image/jpeg',
#         '.gif': 'image/gif',
#         '.webp': 'image/webp',
#         '.svg': 'image/svg+xml'
#     }
    
#     with open(path, 'rb') as image_file:
#         image_data = image_file.read()
#         base64_data = base64.b64encode(image_data).decode('utf-8')
        
#         # 実際のファイル内容からMIMEタイプを判断
#         mime_type = detect_image_type(image_data)
#         if mime_type is None:
#             # ファイル内容から判断できない場合は拡張子から判断
#             ext = os.path.splitext(path)[1].lower()
#             mime_type = mime_types.get(ext, 'image/png')
        
#         return f'data:{mime_type};base64,{base64_data}'
