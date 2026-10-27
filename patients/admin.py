from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("name", "age", "gender", "contact_number", "created_by", "created_at")
    list_filter = ("gender", "created_at")
    search_fields = ("name", "first_name", "last_name", "contact_number", "email", "created_by__email")
    readonly_fields = ("created_at", "updated_at")
