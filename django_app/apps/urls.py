from django.urls import path

from . import views

urlpatterns = [
    # API
    path("api/images/analyze/", views.AnalyzeImageView.as_view(), name="analyze_image"),
    # 画面
    path("", views.ImageUploadView.as_view(), name="image_upload"),
]
