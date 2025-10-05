import django
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView


class LandingPageView(TemplateView):
    """
    Landing page view showing setup congratulations
    """

    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["django_version"] = django.get_version()
        # Add SKELLAR API settings
        from core.config import settings as core_settings

        context["skellar_api_endpoint"] = core_settings.SKELLAR_API_ENDPOINT
        context["skellar_api_key"] = core_settings.SKELLAR_API_KEY

        # Add user information if authenticated
        if self.request.user.is_authenticated:
            context["user_id"] = str(self.request.user.id)
        else:
            context["user_id"] = "anonymous"

        return context


class HealthCheckView(View):
    """
    Simple health check endpoint
    """

    def get(self, request):
        return JsonResponse(
            {
                "status": "ok",
                "message": "Django server is running",
                "version": django.get_version(),
            }
        )


class ImageUploadView(View):
    """
    Placeholder for image upload functionality
    """

    def post(self, request):
        return JsonResponse(
            {"message": "Image upload endpoint - implementation needed"}, status=501
        )


class ImageDetailView(View):
    """
    Placeholder for image detail functionality
    """

    def get(self, request, pk):
        return JsonResponse(
            {
                "message": f"Image detail endpoint for image {pk} - implementation needed"
            },
            status=501,
        )


class UserImagesView(View):
    """
    Placeholder for user images functionality
    """

    def get(self, request):
        return JsonResponse(
            {"message": "User images endpoint - implementation needed"}, status=501
        )
