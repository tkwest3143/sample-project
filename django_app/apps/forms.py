from pathlib import Path

from django import forms

from .serializers import ALLOWED_IMAGE_EXTENSIONS


class ImageUploadForm(forms.Form):
    image_path = forms.CharField(label="画像パス")

    def clean_image_path(self):
        image_path = self.cleaned_data["image_path"]
        ext = Path(image_path).suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise forms.ValidationError(
                f"画像ファイルのパスを入力してください ({', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))})"
            )
        return image_path
