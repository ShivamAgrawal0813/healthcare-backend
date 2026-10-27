from django.contrib import admin
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "specialization", "email", "phone_number", "experience_years", "created_at")
    list_filter = ("specialization", "created_at")
    search_fields = ("name", "first_name", "last_name", "specialization", "email", "phone_number")
    readonly_fields = ("created_at", "updated_at")
