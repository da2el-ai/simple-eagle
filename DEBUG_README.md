# デバッグモード使用方法

## 概要

このプロジェクトでは、デバッグ用のprint文をif文を使わずに制御できるシステムを実装しました。
環境変数 `EAGLE_DEBUG` の値によって、デバッグメッセージの表示/非表示を切り替えることができます。

## 使用方法

### 1. 通常モード（デバッグメッセージ非表示）

```bash
run.bat
```

または、run.batファイル内で：
```batch
set EAGLE_DEBUG=false
```

### 2. デバッグモード（デバッグメッセージ表示）

#### 方法1: 専用のバッチファイルを使用
```bash
run_debug.bat
```

#### 方法2: run.batを編集
run.batファイル内で以下のように変更：
```batch
REM set EAGLE_DEBUG=true  ← この行のコメントアウトを外す
set EAGLE_DEBUG=false     ← この行をコメントアウト
```

### 3. 環境変数を直接設定

```bash
set EAGLE_DEBUG=true
python -m uvicorn index:app --reload --host 0.0.0.0 --port 8000
```

## 実装詳細

### debug_logger.py
- デバッグ用のロガーを設定
- `debug_print()` 関数を提供
- 環境変数 `EAGLE_DEBUG` が `true` の場合のみメッセージを出力

### 変更されたファイル
- `modules/eagle_api.py`: 全てのprint文をdebug_printに置換
- `modules/util.py`: 全てのprint文をdebug_printに置換
- `run.bat`: デバッグモード切り替えのコメントを追加
- `run_debug.bat`: デバッグモード専用のバッチファイル

## メリット

1. **if文不要**: コード内でif文による分岐を書く必要がない
2. **簡単切り替え**: バッチファイルまたは環境変数で簡単に切り替え可能
3. **パフォーマンス**: デバッグモードOFFの場合、ログ処理のオーバーヘッドが最小限
4. **保守性**: デバッグメッセージの追加・削除が簡単

## 使用例

```python
# 従来の方法（if文が必要）
if DEBUG:
    print("デバッグメッセージ")

# 新しい方法（if文不要）
debug_print("デバッグメッセージ")
```

デバッグモードがOFFの場合、`debug_print()` は何も出力せず、パフォーマンスへの影響も最小限です。
