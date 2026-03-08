from django.utils import timezone

from .clients import AiAnalysisClient
from .models import AiAnalysisLog


class ApiError(Exception):
    pass


class AiAnalysisService:
    def __init__(self):
        self.client = AiAnalysisClient()

    def analyze_and_log(self, image_path: str) -> int:
        request_timestamp = timezone.now()
        api_response = self.client.analyze(image_path)
        response_timestamp = timezone.now()

        estimated_data = api_response.get("estimated_data", {})
        log = AiAnalysisLog(
            image_path=image_path,
            success=api_response.get("success", False),
            message=api_response.get("message"),
            estimated_class=estimated_data.get("class"),
            confidence=estimated_data.get("confidence"),
            request_timestamp=request_timestamp,
            response_timestamp=response_timestamp,
        )
        log.save()

        if not api_response.get("success", False):
            raise ApiError(api_response.get("message", "Unknown error"))

        return log.id
