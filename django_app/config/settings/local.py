from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# AI Analysis API
AI_ANALYSIS_BASE_URL = "http://example.com/"
USE_MOCK_AI_API = True
MOCK_AI_RESPONSE_FILE = BASE_DIR / "apps" / "mocks" / "mock_response.json"
