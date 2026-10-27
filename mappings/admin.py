from django.contrib import admin
from .models import PatientDoctorMapping

@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "created_at")
    list_filter = ("created_at",)
    search_fields = ("patient__name", "doctor__name", "doctor__specialization")
    readonly_fields = ("created_at",)
