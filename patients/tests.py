from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User
from .models import Patient

class PatientAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="staff@example.com",
            name="Staff User",
            password="Password123!"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            name="Other User",
            password="Password123!"
        )
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse("patient-list")
        self.patient_payload = {
            "name": "Jane Patient",
            "age": 34,
            "gender": "female",
            "contact_number": "+1234567890",
            "email": "jane.patient@example.com",
            "address": "123 Health Ave, Medical City",
            "medical_history": "Hypertension diagnosed 2021"
        }

    def test_unauthenticated_user_cannot_access_patients(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_patient_success(self):
        response = self.client.post(self.list_url, self.patient_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "Jane")
        self.assertEqual(response.data["last_name"], "Patient")
        self.assertEqual(response.data["age"], 34)

    def test_create_patient_with_single_name(self):
        payload = {
            "name": "Cher",
            "age": 50,
            "gender": "female",
            "medical_history": "Routine checkup"
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "Cher")
        self.assertEqual(response.data["last_name"], "")

    def test_list_patients_only_returns_user_patients(self):
        Patient.objects.create(created_by=self.user, **self.patient_payload)
        Patient.objects.create(
            created_by=self.other_user,
            name="Bob Patient",
            first_name="Bob",
            last_name="Patient",
            age=50,
            gender="male",
            contact_number="+9876543210"
        )

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["first_name"], "Jane")

    def test_get_patient_detail_success(self):
        patient = Patient.objects.create(created_by=self.user, **self.patient_payload)
        detail_url = reverse("patient-detail", kwargs={"pk": patient.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], patient.id)

    def test_cannot_access_other_users_patient(self):
        patient_other = Patient.objects.create(
            created_by=self.other_user,
            name="Secret Patient",
            age=40,
            gender="other",
            contact_number="+111222333"
        )
        detail_url = reverse("patient-detail", kwargs={"pk": patient_other.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_patient_put_treats_as_partial(self):
        patient = Patient.objects.create(created_by=self.user, **self.patient_payload)
        detail_url = reverse("patient-detail", kwargs={"pk": patient.id})
        response = self.client.put(detail_url, {"name": "Jane Updated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        patient.refresh_from_db()
        self.assertEqual(patient.first_name, "Jane")
        self.assertEqual(patient.last_name, "Updated")
        self.assertEqual(patient.address, "123 Health Ave, Medical City")

    def test_update_patient_patch_success(self):
        patient = Patient.objects.create(created_by=self.user, **self.patient_payload)
        detail_url = reverse("patient-detail", kwargs={"pk": patient.id})
        response = self.client.patch(detail_url, {"age": 35, "gender": "other"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        patient.refresh_from_db()
        self.assertEqual(patient.age, 35)
        self.assertEqual(patient.gender, "other")

    def test_delete_patient_success(self):
        patient = Patient.objects.create(created_by=self.user, **self.patient_payload)
        detail_url = reverse("patient-detail", kwargs={"pk": patient.id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(pk=patient.id).exists())

    def test_delete_other_user_patient_forbidden(self):
        patient_other = Patient.objects.create(
            created_by=self.other_user,
            name="Other",
            age=50,
            gender="male"
        )
        detail_url = reverse("patient-detail", kwargs={"pk": patient_other.id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_validation_age_invalid(self):
        response = self.client.post(
            self.list_url,
            {"name": "X", "age": 0, "gender": "male"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("age", response.data)

        response2 = self.client.post(
            self.list_url,
            {"name": "X", "age": 131, "gender": "male"},
            format="json"
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("age", response2.data)

    def test_validation_gender_invalid(self):
        response = self.client.post(
            self.list_url,
            {"name": "X", "age": 20, "gender": "unknown"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("gender", response.data)
