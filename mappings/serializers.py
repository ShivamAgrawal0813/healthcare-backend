from rest_framework import serializers
from .models import PatientDoctorMapping
from patients.models import Patient
from doctors.models import Doctor

class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        source="patient",
        queryset=Patient.objects.all()
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        source="doctor",
        queryset=Doctor.objects.all()
    )
    patient = serializers.StringRelatedField(read_only=True)
    doctor = serializers.StringRelatedField(read_only=True)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    class Meta:
        model = PatientDoctorMapping
        fields = [
            "id",
            "patient_id",
            "doctor_id",
            "patient",
            "doctor",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "patient", "doctor", "created_at"]

    def to_internal_value(self, data):
        # Support both {"patient_id": 1, "doctor_id": 2} and {"patient": 1, "doctor": 2}
        mutable = data.copy() if hasattr(data, "copy") else dict(data)
        if "patient" in mutable and "patient_id" not in mutable:
            mutable["patient_id"] = mutable["patient"]
        if "doctor" in mutable and "doctor_id" not in mutable:
            mutable["doctor_id"] = mutable["doctor"]
        return super().to_internal_value(mutable)

    def validate(self, attrs):
        patient = attrs["patient"]
        doctor = attrs["doctor"]

        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            if patient.created_by != request.user and not request.user.is_staff:
                raise serializers.ValidationError(
                    {"patient_id": "You do not have permission to assign to this patient."}
                )

        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError("This doctor is already assigned to the patient.")

        return attrs
