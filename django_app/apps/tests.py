"""
テスト分類:
  ユニットテスト    - 個々のクラス・メソッドの動作を単独で検証 (DB なし or モック)
  統合テスト        - 複数コンポーネントを組み合わせた動作を検証 (DB あり)
"""

import json
import urllib.error
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .clients import AiAnalysisClient
from .forms import ImageUploadForm
from .models import AiAnalysisLog
from .serializers import AnalyzeImageRequest
from .services import AiAnalysisService, ApiError

MOCKS_DIR = Path(__file__).parent / "mocks"

IMAGE_PATH = "/image/d03f1d36ca69348c51aa/c413eac329e1c0d03/test.jpg"

SUCCESS_RESPONSE = {
    "success": True,
    "message": "success",
    "estimated_data": {"class": 3, "confidence": 0.8683},
}
FAILURE_RESPONSE = {
    "success": False,
    "message": "Error:E50012",
    "estimated_data": {},
}


# ---------------------------------------------------------------------------
# ユニットテスト: AnalyzeImageRequest (シリアライザー)
# ---------------------------------------------------------------------------
class AnalyzeImageRequestTest(TestCase):
    def _from_body(self, body: dict):
        return AnalyzeImageRequest.from_body(json.dumps(body).encode())

    # 正常な jpg パスを受け付ける
    def test_valid_jpg_path_returns_request(self):
        req, errors = self._from_body({"image_path": "/images/test.jpg"})
        self.assertIsNotNone(req)
        self.assertEqual(errors, {})
        self.assertEqual(req.image_path, "/images/test.jpg")

    # 正常な png パスを受け付ける
    def test_valid_png_path_returns_request(self):
        req, errors = self._from_body({"image_path": "/images/test.png"})
        self.assertIsNotNone(req)
        self.assertEqual(errors, {})

    # 許可拡張子がすべて受け付けられる
    def test_valid_extensions_are_accepted(self):
        for ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
            with self.subTest(ext=ext):
                req, errors = self._from_body({"image_path": f"/images/test{ext}"})
                self.assertIsNotNone(req)
                self.assertEqual(errors, {})

    # 画像以外の拡張子はエラーを返す
    def test_non_image_extension_returns_error(self):
        req, errors = self._from_body({"image_path": "/images/test.txt"})
        self.assertIsNone(req)
        self.assertIn("error", errors)

    # image_path がない場合はエラーを返す
    def test_missing_image_path_returns_error(self):
        req, errors = self._from_body({})
        self.assertIsNone(req)
        self.assertIn("error", errors)

    # 不正な JSON はエラーを返す
    def test_invalid_json_returns_error(self):
        req, errors = AnalyzeImageRequest.from_body(b"not json")
        self.assertIsNone(req)
        self.assertIn("error", errors)

    # 拡張子の大文字小文字を区別しない
    def test_extension_check_is_case_insensitive(self):
        req, errors = self._from_body({"image_path": "/images/test.JPG"})
        self.assertIsNotNone(req)
        self.assertEqual(errors, {})


# ---------------------------------------------------------------------------
# ユニットテスト: ImageUploadForm (ビュー用フォーム)
# ---------------------------------------------------------------------------
class ImageUploadFormTest(TestCase):
    # 正常な jpg パスはバリデーションを通過する
    def test_valid_jpg_path_is_accepted(self):
        form = ImageUploadForm(data={"image_path": "/images/test.jpg"})
        self.assertTrue(form.is_valid())

    # 許可拡張子がすべて受け付けられる
    def test_valid_extensions_are_accepted(self):
        for ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
            with self.subTest(ext=ext):
                form = ImageUploadForm(data={"image_path": f"/images/test{ext}"})
                self.assertTrue(form.is_valid())

    # 画像以外の拡張子はエラーになる
    def test_non_image_extension_is_rejected(self):
        form = ImageUploadForm(data={"image_path": "/images/test.txt"})
        self.assertFalse(form.is_valid())
        self.assertIn("image_path", form.errors)

    # 空文字はエラーになる
    def test_empty_path_is_rejected(self):
        form = ImageUploadForm(data={"image_path": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("image_path", form.errors)

    # 拡張子の大文字小文字を区別しない
    def test_extension_check_is_case_insensitive(self):
        form = ImageUploadForm(data={"image_path": "/images/test.JPG"})
        self.assertTrue(form.is_valid())


# ---------------------------------------------------------------------------
# ユニットテスト: モデル
# ---------------------------------------------------------------------------
class AiAnalysisLogModelTest(TestCase):
    # テーブル名が ai_analysis_log に設定されている
    def test_db_table_name(self):
        self.assertEqual(AiAnalysisLog._meta.db_table, "ai_analysis_log")

    # estimated_class フィールドの DB カラム名が class になっている
    def test_class_column_name(self):
        field = AiAnalysisLog._meta.get_field("estimated_class")
        self.assertEqual(field.column, "class")


# ---------------------------------------------------------------------------
# ユニットテスト: AiAnalysisClient (モックモード)
# ---------------------------------------------------------------------------
@override_settings(USE_MOCK_AI_API=True)
class AiAnalysisClientMockTest(TestCase):
    # モックファイルから成功レスポンスを読み込んで返す
    @override_settings(MOCK_AI_RESPONSE_FILE=MOCKS_DIR / "mock_response_success.json")
    def test_mock_returns_success(self):
        result = AiAnalysisClient().analyze(IMAGE_PATH)
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "success")
        self.assertIn("class", result["estimated_data"])
        self.assertIn("confidence", result["estimated_data"])

    # モックファイルから失敗レスポンスを読み込んで返す
    @override_settings(MOCK_AI_RESPONSE_FILE=MOCKS_DIR / "mock_response_failure.json")
    def test_mock_returns_failure(self):
        result = AiAnalysisClient().analyze(IMAGE_PATH)
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Error:E50012")
        self.assertEqual(result["estimated_data"], {})

    # モックファイルが存在しない場合は FileNotFoundError を送出する
    @override_settings(MOCK_AI_RESPONSE_FILE="/nonexistent/path/response.json")
    def test_mock_raises_when_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            AiAnalysisClient().analyze(IMAGE_PATH)


# ---------------------------------------------------------------------------
# ユニットテスト: AiAnalysisClient (実 API モード / HTTP 通信をモック)
# ---------------------------------------------------------------------------
@override_settings(USE_MOCK_AI_API=False, AI_ANALYSIS_BASE_URL="http://example.com/")
class AiAnalysisClientRealApiTest(TestCase):
    # POST リクエストを送信し、成功レスポンスをそのまま返す
    def test_calls_api_and_returns_success_response(self):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(SUCCESS_RESPONSE).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            result = AiAnalysisClient().analyze(IMAGE_PATH)

        mock_open.assert_called_once()
        request_arg = mock_open.call_args[0][0]
        self.assertEqual(request_arg.get_method(), "POST")
        self.assertIn(b"image_path", request_arg.data)
        self.assertTrue(result["success"])
        self.assertEqual(result["estimated_data"]["class"], 3)

    # API が失敗レスポンスを返した場合はそのまま返す
    def test_calls_api_and_returns_failure_response(self):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(FAILURE_RESPONSE).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = AiAnalysisClient().analyze(IMAGE_PATH)

        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Error:E50012")

    # HTTP エラー (5xx 等) が発生した場合はエラーレスポンスを返す
    def test_http_error_returns_error_response(self):
        http_err = urllib.error.HTTPError(
            url="http://example.com/",
            code=500,
            msg="Internal Server Error",
            hdrs={},
            fp=MagicMock(read=lambda: b'{"success": false, "message": "server error", "estimated_data": {}}'),
        )
        with patch("urllib.request.urlopen", side_effect=http_err):
            result = AiAnalysisClient().analyze(IMAGE_PATH)

        self.assertFalse(result["success"])

    # 接続エラーが発生した場合はエラーレスポンスを返す
    def test_connection_error_returns_error_response(self):
        with patch("urllib.request.urlopen", side_effect=Exception("Connection refused")):
            result = AiAnalysisClient().analyze(IMAGE_PATH)

        self.assertFalse(result["success"])
        self.assertIn("Connection refused", result["message"])


# ---------------------------------------------------------------------------
# 統合テスト: AiAnalysisService (DB あり、HTTP クライアントをモック)
# ---------------------------------------------------------------------------
@override_settings(USE_MOCK_AI_API=False)
class AiAnalysisServiceTest(TestCase):
    # API 成功時にログを DB に保存し、採番された ID を返す
    def test_success_saves_log_and_returns_id(self):
        with patch("apps.services.AiAnalysisClient") as MockClient:
            MockClient.return_value.analyze.return_value = SUCCESS_RESPONSE
            log_id = AiAnalysisService().analyze_and_log(IMAGE_PATH)

        self.assertIsInstance(log_id, int)
        log = AiAnalysisLog.objects.get(pk=log_id)
        self.assertEqual(log.image_path, IMAGE_PATH)
        self.assertTrue(log.success)
        self.assertEqual(log.estimated_class, 3)
        self.assertEqual(log.confidence, Decimal("0.8683"))
        self.assertIsNotNone(log.request_timestamp)
        self.assertIsNotNone(log.response_timestamp)
        self.assertLessEqual(log.request_timestamp, log.response_timestamp)

    # API 失敗時はログを DB に保存した上で ApiError を送出する
    def test_failure_saves_log_and_raises_api_error(self):
        with patch("apps.services.AiAnalysisClient") as MockClient:
            MockClient.return_value.analyze.return_value = FAILURE_RESPONSE
            with self.assertRaises(ApiError) as ctx:
                AiAnalysisService().analyze_and_log(IMAGE_PATH)

        self.assertEqual(str(ctx.exception), "Error:E50012")
        log = AiAnalysisLog.objects.get()
        self.assertFalse(log.success)
        self.assertIsNone(log.estimated_class)
        self.assertIsNone(log.confidence)


# ---------------------------------------------------------------------------
# 統合テスト: ビュー (HTTP レベルの振る舞いを検証、サービスをモック)
# ---------------------------------------------------------------------------
@override_settings(USE_MOCK_AI_API=False)
class AnalyzeImageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("analyze_image")

    def setUp(self):
        self.client = Client()

    def _post(self, body):
        return self.client.post(
            self.url,
            data=json.dumps(body),
            content_type="application/json",
        )

    # 正常リクエスト時は 200 と id を返す
    def test_success_returns_200_with_id(self):
        with patch("apps.services.AiAnalysisClient") as MockClient:
            MockClient.return_value.analyze.return_value = SUCCESS_RESPONSE
            response = self._post({"image_path": IMAGE_PATH})

        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())

    # API 失敗時は 502 とエラーメッセージを返す
    def test_failure_returns_502_with_error(self):
        with patch("apps.services.AiAnalysisClient") as MockClient:
            MockClient.return_value.analyze.return_value = FAILURE_RESPONSE
            response = self._post({"image_path": IMAGE_PATH})

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["error"], "Error:E50012")

    # image_path が未指定の場合は 400 を返す
    def test_missing_image_path_returns_400(self):
        response = self._post({})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    # リクエストボディが不正な JSON の場合は 400 を返す
    def test_invalid_json_returns_400(self):
        response = self.client.post(self.url, data="not json", content_type="application/json")
        self.assertEqual(response.status_code, 400)

    # GET メソッドは許可されず 405 を返す
    def test_get_method_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    # リクエストごとにログが 1 件ずつ DB に保存される
    def test_each_request_creates_one_log(self):
        with patch("apps.services.AiAnalysisClient") as MockClient:
            MockClient.return_value.analyze.return_value = SUCCESS_RESPONSE
            self._post({"image_path": IMAGE_PATH})
            self._post({"image_path": IMAGE_PATH})

        self.assertEqual(AiAnalysisLog.objects.count(), 2)
