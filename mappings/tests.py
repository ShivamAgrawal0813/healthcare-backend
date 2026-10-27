from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User
from patients.models import Patient
from doctors.models import Doctor
from .models import PatientDoctorMapping

class PatientDoctorMappingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="staff.user@clinic.com",
            name="Clinic Staff",
            password="Password123!"
        )
        self.other_user = User.objects.create_user(
            email="other.staff@clinic.com",
            name="Other Staff",
            password="Password123!"
        )
        self.client.force_authenticate(user=self.user)

        self.patient = Patient.objects.create(
            created_by=self.user,
            name="Alice Patient",
            first_name="Alice",
            last_name="Patient",
            age=28,
            gender="female",
            contact_number="+1000000000"
        )
        self.doctor1 = Doctor.objects.create(
            name="John Watson",
            first_name="John",
            last_name="Watson",
            specialization="General Medicine",
            email="watson@bakerstreet.com",
            phone_number="+1000000001",
            experience_years=10
        )
        self.doctor2 = Doctor.objects.create(
            name="Stephen Strange",
            first_name="Stephen",
            last_name="Strange",
            specialization="Neuro Surgery",
            email="strange@sanctum.com",
            phone_number="+1000000002",
            experience_years=15
        )
        self.mappings_url = reverse("mapping-list-create")

    def test_assign_doctor_to_patient_success(self):
        payload = {
            "patient_id": self.patient.id,
            "doctor_id": self.doctor1.id,
            "notes": "Initial consultation assigned."
        }
        response = self.client.post(self.mappings_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["patient_id"], self.patient.id)
        self.assertEqual(response.data["doctor_id"], self.doctor1.id)
        self.assertTrue(PatientDoctorMapping.objects.filter(patient=self.patient, doctor=self.doctor1).exists())

    def test_duplicate_mapping_rejected(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)
        payload = {
            "patient_id": self.patient.id,
            "doctor_id": self.doctor1.id
        }
        response = self.client.post(self.mappings_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_cannot_assign_doctor_to_unowned_patient(self):
        other_patient = Patient.objects.create(
            created_by=self.other_user,
            name="Foreign Patient",
            first_name="Foreign",
            last_name="Patient",
            age=45,
            gender="male",
            contact_number="+9999999999"
        )
        payload = {
            "patient_id": other_patient.id,
            "doctor_id": self.doctor1.id
        }
        response = self.client.post(self.mappings_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("patient_id", response.data)

    def test_get_all_mappings_only_own(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)
        other_patient = Patient.objects.create(
            created_by=self.other_user,
            name="Other",
            first_name="Other",
            last_name="Patient",
            age=30,
            gender="male"
        )
        PatientDoctorMapping.objects.create(patient=other_patient, doctor=self.doctor2)

        response = self.client.get(self.mappings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)

    def test_get_doctors_assigned_to_specific_patient(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor2)

        patient_mapping_url = reverse(
            "mapping-detail-or-patient",
            kwargs={"pk": self.patient.id}
        )
        response = self.client.get(patient_mapping_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_remove_doctor_from_patient_by_mapping_id(self):
        mapping = PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)
        delete_url = reverse(
            "mapping-detail-or-patient",
            kwargs={"pk": mapping.id}
        )
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PatientDoctorMapping.objects.filter(pk=mapping.id).exists())

    def test_unauthenticated_mapping_forbidden(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.mappings_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
