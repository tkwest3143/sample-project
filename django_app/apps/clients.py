import json
import urllib.error
import urllib.request

from django.conf import settings

# API仕様
# ベースURL : settings.AI_ANALYSIS_BASE_URL (例: http://example.com/)
# メソッド  : POST
# パラメーター: image_path (String) 例) /image/d03f1d36ca69348c51aa/c413eac329e1c0d03/test.jpg


class AiAnalysisClient:
    def analyze(self, image_path: str) -> dict:
        if getattr(settings, "USE_MOCK_AI_API", False):
            return self._mock_response()
        return self._call_api(image_path)

    def _call_api(self, image_path: str) -> dict:
        url = settings.AI_ANALYSIS_BASE_URL
        payload = json.dumps({"image_path": image_path}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return {"success": False, "message": f"HTTP {e.code}", "estimated_data": {}}
        except Exception as e:
            return {"success": False, "message": str(e), "estimated_data": {}}

    def _mock_response(self) -> dict:
        with open(settings.MOCK_AI_RESPONSE_FILE, encoding="utf-8") as f:
            return json.load(f)
