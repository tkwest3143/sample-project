import json
from dataclasses import dataclass
from pathlib import Path

# 許可する画像拡張子
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


@dataclass
class AnalyzeImageRequest:
    image_path: str

    @classmethod
    def from_body(cls, body: bytes) -> tuple["AnalyzeImageRequest | None", dict]:
        try:
            data = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            return None, {"error": "Invalid JSON body"}

        image_path = data.get("image_path")
        if not image_path:
            return None, {"error": "image_path は必須です"}

        # 画像ファイルの拡張子チェック
        ext = Path(image_path).suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            allowed = ", ".join(sorted(ALLOWED_IMAGE_EXTENSIONS))
            return None, {"error": f"image_path には画像ファイルのパスを指定してください ({allowed})"}

        return cls(image_path=image_path), {}
