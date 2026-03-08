import os

from .base import *

DEBUG = False

ALLOWED_HOSTS = os.environ["DJANGO_ALLOWED_HOSTS"].split(",")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# AI Analysis API
AI_ANALYSIS_BASE_URL = os.environ["AI_ANALYSIS_BASE_URL"]
USE_MOCK_AI_API = False
