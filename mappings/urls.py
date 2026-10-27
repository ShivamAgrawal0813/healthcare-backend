from django.urls import path
from .views import (
    PatientDoctorMappingListCreateView,
    PatientDoctorMappingDetailAndPatientDoctorsView,
)

urlpatterns = [
    path("", PatientDoctorMappingListCreateView.as_view(), name="mapping-list-create"),
    path("<int:pk>/", PatientDoctorMappingDetailAndPatientDoctorsView.as_view(), name="mapping-detail-or-patient"),
    path("patient/<int:pk>/", PatientDoctorMappingDetailAndPatientDoctorsView.as_view(), name="mapping-patient-doctors"),
]
