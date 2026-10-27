from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import PatientDoctorMapping
from .serializers import PatientDoctorMappingSerializer
from patients.models import Patient

class PatientDoctorMappingListCreateView(generics.ListCreateAPIView):
    """
    POST /api/mappings/ - Assign a doctor to a patient.
    GET /api/mappings/ - Retrieve all patient-doctor mappings for the authenticated user's patients.
    """
    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return PatientDoctorMapping.objects.all().select_related("patient", "doctor")
        return PatientDoctorMapping.objects.filter(
            patient__created_by=self.request.user
        ).select_related("patient", "doctor")

class PatientDoctorMappingDetailAndPatientDoctorsView(generics.GenericAPIView):
    """
    Handles both:
    - GET /api/mappings/<patient_id>/ - Get all doctors assigned to a specific patient.
    - DELETE /api/mappings/<id>/ - Remove a doctor from a patient (delete mapping by ID).
    """
    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return PatientDoctorMapping.objects.all().select_related("patient", "doctor")
        return PatientDoctorMapping.objects.filter(
            patient__created_by=self.request.user
        ).select_related("patient", "doctor")

    def get(self, request, pk: int, *args, **kwargs):
        # 1. First treat pk as patient_id
        patient_query = Patient.objects.filter(pk=pk)
        if not request.user.is_staff:
            patient_query = patient_query.filter(created_by=request.user)

        patient = patient_query.first()
        if patient:
            mappings = self.get_queryset().filter(patient=patient)
            serializer = self.get_serializer(mappings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 2. Alternatively check if pk is a mapping ID
        try:
            mapping = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(mapping)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PatientDoctorMapping.DoesNotExist:
            return Response(
                {"detail": f"Patient or mapping with id {pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk: int, *args, **kwargs):
        # Treat pk as mapping id
        try:
            mapping = self.get_queryset().get(pk=pk)
        except PatientDoctorMapping.DoesNotExist:
            return Response(
                {"detail": f"Mapping with id {pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
