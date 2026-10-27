from django.contrib import admin
from django.urls import path, include
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class APIRootView(APIView):
    """
    Healthcare Backend API Root
    """
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return Response({
            "service": "Healthcare Application Backend API",
            "version": "1.0.0",
            "status": "Healthy",
            "endpoints": {
                "authentication": {
                    "register": "/api/auth/register/",
                    "login": "/api/auth/login/",
                    "token_refresh": "/api/auth/token/refresh/",
                    "current_user": "/api/auth/me/"
                },
                "patients": {
                    "list_or_create": "/api/patients/",
                    "detail_update_delete": "/api/patients/<id>/"
                },
                "doctors": {
                    "list_or_create": "/api/doctors/",
                    "detail_update_delete": "/api/doctors/<id>/"
                },
                "mappings": {
                    "list_or_create": "/api/mappings/",
                    "patient_doctors_or_detail": "/api/mappings/<patient_id>/",
                    "delete_mapping": "/api/mappings/<id>/"
                }
            }
        })

urlpatterns = [
    path("", APIRootView.as_view(), name="api-root"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    path("api/patients/", include("patients.urls")),
    path("api/doctors/", include("doctors.urls")),
    path("api/mappings/", include("mappings.urls")),
]
