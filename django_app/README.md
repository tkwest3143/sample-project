# Django AI Analysis API

画像ファイルのパスを受け取り、外部 AI 分析 API を呼び出して結果を DB に保存する Django アプリ。

## セットアップ

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # DJANGO_SECRET_KEY を設定
python manage.py migrate
```

## 起動

```bash
python manage.py runserver
```

## エンドポイント

### API

| Method | URL | 説明 |
|--------|-----|------|
| POST | `/api/images/analyze/` | AI 分析を実行して結果を保存 |

**リクエスト**
```json
{ "image_path": "/image/xxx/test.jpg" }
```

**レスポンス（成功）**
```json
{ "id": 42 }
```

**レスポンス（失敗）**
```json
{ "error": "Error:E50012" }
```

### 画面

| URL | 説明 |
|-----|------|
| `/` | 画像パス入力・AI 分析実行画面 |

## 設定

`config/settings/local.py` の `USE_MOCK_AI_API` で実 API とモックを切り替えます。

```python
USE_MOCK_AI_API = True   # モック（デフォルト）
USE_MOCK_AI_API = False  # 実際の API を呼び出す
```

## テスト

```bash
python manage.py test apps --settings=config.settings.local
```

## Lint

```bash
ruff check .
```
