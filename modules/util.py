import base64
import os
from PIL import Image
import io

def detect_image_type(data: bytes) -> str:
    """
    画像データの内容からMIMEタイプを判断
    """
    if data.startswith(b'RIFF') and b'WEBP' in data[0:12]:
        return 'image/webp'
    elif data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png'
    elif data.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'
    elif data.startswith(b'GIF87a') or data.startswith(b'GIF89a'):
        return 'image/gif'
    return None

def load_image(path: str, max_file_size=0, quality=85):
    """
    ローカルファイルパスから画像を読み込む
    - path: 画像パス
    - max_file_size: ファイルサイズがこの値より大きかったらjpeg圧縮をかける。0なら圧縮しない（KB単位）
    - quality: jpeg圧縮率
    - 戻り値: (バイナリデータ, Content-Type)のタプル
    """
    try:
        with open(path, 'rb') as image_file:
            content = image_file.read()
        
        # ファイルサイズをKB単位で計算
        file_size_kb = len(content) / 1024
        
        # max_file_sizeが0でない場合、かつファイルサイズが制限を超える場合は圧縮
        if max_file_size > 0 and file_size_kb > max_file_size:
            # PILで画像を開く
            image = Image.open(path)
            
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
        else:
            # 圧縮しない場合は元のファイル拡張子からContent-Typeを判断
            content_type = 'image/webp' if path.endswith('.webp') \
                          else 'image/png' if path.endswith('.png') \
                          else 'image/jpeg' if path.endswith(('.jpg', '.jpeg')) \
                          else 'image/gif' if path.endswith('.gif') \
                          else 'application/octet-stream'
        
        return content, content_type
        
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        raise

def filepath_to_base64(path:str):
    """
    ローカルファイルパスから画像を読み込み Base64で返す
    """
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml'
    }
    
    with open(path, 'rb') as image_file:
        image_data = image_file.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        
        # 実際のファイル内容からMIMEタイプを判断
        mime_type = detect_image_type(image_data)
        if mime_type is None:
            # ファイル内容から判断できない場合は拡張子から判断
            ext = os.path.splitext(path)[1].lower()
            mime_type = mime_types.get(ext, 'image/png')
        
        return f'data:{mime_type};base64,{base64_data}'
