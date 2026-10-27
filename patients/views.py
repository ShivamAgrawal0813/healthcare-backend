from rest_framework import viewsets, permissions
from .models import Patient
from .serializers import PatientSerializer

class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing patient records.
    GET /api/patients/ - Retrieve all patients created by the authenticated user.
    POST /api/patients/ - Add a new patient (Authenticated users only).
    GET /api/patients/<id>/ - Get details of a specific patient.
    PUT /api/patients/<id>/ - Update patient details.
    DELETE /api/patients/<id>/ - Delete a patient record.
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Authenticated users only see and manage their own patients
        if self.request.user.is_authenticated:
            return Patient.objects.filter(created_by=self.request.user)
        return Patient.objects.none()

    def update(self, request, *args, **kwargs):
        """
        Treat PUT as partial update so clients can update specific fields
        without needing to re-send all required fields.
        """
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)
