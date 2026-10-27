from django.db import models
from django.conf import settings

class Doctor(models.Model):
    name = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=255)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, default="")
    experience_years = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_doctors"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["first_name", "last_name", "name"]

    @property
    def years_of_experience(self):
        return self.experience_years

    @years_of_experience.setter
    def years_of_experience(self, val):
        self.experience_years = val

    def save(self, *args, **kwargs):
        # Synchronize name with first_name and last_name
        if not self.name and (self.first_name or self.last_name):
            self.name = f"{self.first_name} {self.last_name}".strip()
        elif self.name and not (self.first_name or self.last_name):
            parts = self.name.strip().split(" ", 1)
            self.first_name = parts[0]
            self.last_name = parts[1] if len(parts) > 1 else ""
        super().save(*args, **kwargs)

    def __str__(self):
        full = f"{self.first_name} {self.last_name}".strip() or self.name
        return f"Dr. {full} - {self.specialization}"
