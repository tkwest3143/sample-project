from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .forms import ImageUploadForm
from .serializers import AnalyzeImageRequest
from .services import AiAnalysisService, ApiError


@method_decorator(csrf_exempt, name="dispatch")
class AnalyzeImageView(View):
    def post(self, request):
        req_data, errors = AnalyzeImageRequest.from_body(request.body)
        if errors:
            return JsonResponse(errors, status=400)

        try:
            log_id = AiAnalysisService().analyze_and_log(req_data.image_path)
        except ApiError as e:
            return JsonResponse({"error": str(e)}, status=502)

        return JsonResponse({"id": log_id})


class ImageUploadView(View):
    template_name = "apps/analyze.html"

    def get(self, request):
        return render(request, self.template_name, {"form": ImageUploadForm()})

    def post(self, request):
        form = ImageUploadForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form}, status=400)

        image_path = form.cleaned_data["image_path"]

        try:
            log_id = AiAnalysisService().analyze_and_log(image_path)
        except ApiError as e:
            return render(request, self.template_name, {"form": form, "error": str(e)}, status=502)

        return render(request, self.template_name, {"form": ImageUploadForm(), "result": {"id": log_id}})
