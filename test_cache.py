#!/usr/bin/env python3
"""
キャッシュシステムのテスト用スクリプト
"""

import os
import time
from modules.util import load_image, cleanup_expired_cache
from modules.debug_logger import debug_print

def test_cache_system():
    """キャッシュシステムのテスト"""
    print("=== キャッシュシステムのテスト開始 ===")
    
    # 利用可能な画像ファイルを検索
    image_extensions = ['.webp', '.jpg', '.jpeg', '.png', '.gif']
    test_image_path = None
    
    for ext in image_extensions:
        for file in os.listdir('.'):
            if file.lower().endswith(ext):
                test_image_path = file
                break
        if test_image_path:
            break
    
    if test_image_path is None:
        print("テスト用の画像ファイルが見つかりません。")
        print("jpg, jpeg, png, gif, webp形式の画像ファイルを配置してください。")
        return
    
    print(f"テスト画像: {test_image_path}")
    
    # テスト1: 圧縮ありのケース（キャッシュ対象）
    print("\n=== テスト1: 圧縮ありのケース（キャッシュ対象） ===")
    print("--- 1回目の読み込み（キャッシュなし） ---")
    start_time = time.time()
    content1, content_type1 = load_image(test_image_path, max_file_size=500, quality=80)
    end_time = time.time()
    print(f"読み込み時間: {end_time - start_time:.3f}秒")
    print(f"データサイズ: {len(content1)} bytes")
    print(f"Content-Type: {content_type1}")
    
    print("--- 2回目の読み込み（キャッシュあり） ---")
    start_time = time.time()
    content2, content_type2 = load_image(test_image_path, max_file_size=500, quality=80)
    end_time = time.time()
    print(f"読み込み時間: {end_time - start_time:.3f}秒")
    print(f"データサイズ: {len(content2)} bytes")
    print(f"Content-Type: {content_type2}")
    
    # データが同じかチェック
    if content1 == content2 and content_type1 == content_type2:
        print("✓ 圧縮ありのキャッシュが正常に動作しています")
    else:
        print("✗ 圧縮ありのキャッシュに問題があります")
    
    # テスト2: 圧縮なしのケース（キャッシュ対象外）
    print("\n=== テスト2: 圧縮なしのケース（キャッシュ対象外） ===")
    print("--- 1回目の読み込み（圧縮なし） ---")
    start_time = time.time()
    content3, content_type3 = load_image(test_image_path, max_file_size=0, quality=80)
    end_time = time.time()
    print(f"読み込み時間: {end_time - start_time:.3f}秒")
    print(f"データサイズ: {len(content3)} bytes")
    print(f"Content-Type: {content_type3}")
    
    print("--- 2回目の読み込み（圧縮なし） ---")
    start_time = time.time()
    content4, content_type4 = load_image(test_image_path, max_file_size=0, quality=80)
    end_time = time.time()
    print(f"読み込み時間: {end_time - start_time:.3f}秒")
    print(f"データサイズ: {len(content4)} bytes")
    print(f"Content-Type: {content_type4}")
    
    # データが同じかチェック
    if content3 == content4 and content_type3 == content_type4:
        print("✓ 圧縮なしの読み込みが正常に動作しています")
    else:
        print("✗ 圧縮なしの読み込みに問題があります")
    
    # キャッシュディレクトリの確認
    print(f"\n--- キャッシュディレクトリの確認 ---")
    cache_dir = "cache"
    if os.path.exists(cache_dir):
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.cache')]
        print(f"キャッシュファイル数: {len(cache_files)}")
        for cache_file in cache_files:
            cache_path = os.path.join(cache_dir, cache_file)
            cache_size = os.path.getsize(cache_path)
            print(f"  {cache_file}: {cache_size} bytes")
    else:
        print("キャッシュディレクトリが存在しません")
    
    # クリーンアップテスト
    print(f"\n--- クリーンアップテスト ---")
    cleanup_expired_cache()
    print("クリーンアップが完了しました")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_cache_system()
