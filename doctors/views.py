from rest_framework import viewsets, permissions
from .models import Doctor
from .serializers import DoctorSerializer

class DoctorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing doctor records.
    GET /api/doctors/ - Retrieve all doctors (public/browseable).
    POST /api/doctors/ - Add a new doctor (Authenticated users only).
    GET /api/doctors/<id>/ - Get details of a specific doctor (public).
    PUT /api/doctors/<id>/ - Update doctor details (Authenticated users only).
    DELETE /api/doctors/<id>/ - Delete a doctor record (Authenticated users only).
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        """
        Treat PUT as partial update so clients can update specific fields.
        """
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)
