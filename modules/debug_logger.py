import logging
import os
import sys

def setup_debug_logger():
    """
    デバッグロガーを設定
    環境変数 EAGLE_DEBUG が 'true' の場合のみデバッグメッセージを表示
    """
    # デバッグモードの判定
    debug_mode = os.getenv('EAGLE_DEBUG', 'false').lower() == 'true'
    
    # ロガーの設定
    logger = logging.getLogger('eagle_debug')
    logger.setLevel(logging.DEBUG if debug_mode else logging.WARNING)
    
    # 既存のハンドラーをクリア
    logger.handlers.clear()
    
    if debug_mode:
        # コンソールハンドラーを追加
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # フォーマッターを設定
        formatter = logging.Formatter('[DEBUG] %(message)s')
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    
    return logger

# グローバルなデバッグロガーインスタンス
debug_logger = setup_debug_logger()

def debug_print(*args, **kwargs):
    """
    デバッグモードの時のみ出力するprint関数の代替
    使用方法: debug_print("デバッグメッセージ")
    """
    if debug_logger.isEnabledFor(logging.DEBUG):
        # print関数と同じように複数の引数を処理
        message = ' '.join(str(arg) for arg in args)
        debug_logger.debug(message)
