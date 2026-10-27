from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User
from .models import Doctor

class DoctorAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="admin.user@example.com",
            name="Admin User",
            password="Password123!"
        )
        self.list_url = reverse("doctor-list")
        self.doctor_payload = {
            "name": "Gregory House",
            "specialization": "Diagnostic Medicine",
            "email": "dr.house@princeton.edu",
            "phone_number": "+15551234567",
            "experience_years": 20
        }

    def test_unauthenticated_cannot_create_doctor(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.list_url, self.doctor_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_doctors_public(self):
        self.client.force_authenticate(user=None)
        Doctor.objects.create(
            name="Public Doctor",
            first_name="Public",
            last_name="Doctor",
            specialization="General",
            email="public@doctor.com"
        )
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertGreaterEqual(len(results), 1)

    def test_create_doctor_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, self.doctor_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "Gregory")
        self.assertEqual(response.data["last_name"], "House")
        self.assertEqual(response.data["specialization"], "Diagnostic Medicine")
        self.assertEqual(response.data["experience_years"], 20)

    def test_create_doctor_without_email_and_phone(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "name": "Dr Who",
            "specialization": "Time Medicine"
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "Dr")
        self.assertEqual(response.data["last_name"], "Who")

    def test_get_doctor_detail(self):
        doctor = Doctor.objects.create(
            name="James Wilson",
            first_name="James",
            last_name="Wilson",
            specialization="Oncology",
            email="dr.wilson@princeton.edu"
        )
        detail_url = reverse("doctor-detail", kwargs={"pk": doctor.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "dr.wilson@princeton.edu")

    def test_update_doctor_put_treats_as_partial(self):
        self.client.force_authenticate(user=self.user)
        doctor = Doctor.objects.create(
            name="Old Doc",
            first_name="Old",
            last_name="Doc",
            specialization="General",
            email="old.doc@example.com",
            experience_years=5
        )
        detail_url = reverse("doctor-detail", kwargs={"pk": doctor.id})
        response = self.client.put(detail_url, {"name": "New Doc"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doctor.refresh_from_db()
        self.assertEqual(doctor.first_name, "New")
        self.assertEqual(doctor.last_name, "Doc")
        self.assertEqual(doctor.experience_years, 5)

    def test_update_doctor_patch(self):
        self.client.force_authenticate(user=self.user)
        doctor = Doctor.objects.create(
            name="Doc One",
            first_name="Doc",
            last_name="One",
            specialization="General",
            email="doc.one@example.com"
        )
        detail_url = reverse("doctor-detail", kwargs={"pk": doctor.id})
        response = self.client.patch(detail_url, {"specialization": "Surgery"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doctor.refresh_from_db()
        self.assertEqual(doctor.specialization, "Surgery")

    def test_delete_doctor_success(self):
        self.client.force_authenticate(user=self.user)
        doctor = Doctor.objects.create(
            name="Delete Me",
            first_name="Delete",
            last_name="Me",
            specialization="General",
            email="del@doctor.com"
        )
        detail_url = reverse("doctor-detail", kwargs={"pk": doctor.id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Doctor.objects.filter(pk=doctor.id).exists())

    def test_duplicate_email_case_insensitive_rejected(self):
        self.client.force_authenticate(user=self.user)
        Doctor.objects.create(
            name="Doc Existing",
            first_name="Doc",
            last_name="Existing",
            specialization="Cardiology",
            email="unique@hospital.com"
        )
        response = self.client.post(
            self.list_url,
            {
                "name": "Doc Duplicate",
                "specialization": "Cardiology",
                "email": "UNIQUE@HOSPITAL.COM"
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
