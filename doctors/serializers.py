from rest_framework import serializers
from .models import Doctor

class DoctorSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, default="")
    experience_years = serializers.IntegerField(required=False, default=0)
    years_of_experience = serializers.IntegerField(source="experience_years", required=False)

    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "first_name",
            "last_name",
            "specialization",
            "experience_years",
            "years_of_experience",
            "email",
            "phone_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_email(self, value):
        if not value:
            return None
        normalized = value.strip().lower()
        qs = Doctor.objects.filter(email__iexact=normalized)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A doctor with this email already exists.")
        return normalized

    def validate_experience_years(self, value):
        if value < 0 or value > 80:
            raise serializers.ValidationError("Years of experience must be between 0 and 80.")
        return value

    def create(self, validated_data):
        full_name = validated_data.pop("name", None)
        first_name = validated_data.get("first_name", "")
        last_name = validated_data.get("last_name", "")

        if full_name:
            full_name = full_name.strip()
            if " " in full_name:
                first_name, last_name = full_name.split(" ", 1)
            else:
                first_name = full_name
                last_name = ""
        elif first_name or last_name:
            full_name = f"{first_name} {last_name}".strip()

        validated_data["name"] = full_name or first_name
        validated_data["first_name"] = first_name
        validated_data["last_name"] = last_name

        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            validated_data["created_by"] = user

        return Doctor.objects.create(**validated_data)

    def update(self, instance, validated_data):
        full_name = validated_data.pop("name", None)
        if full_name is not None:
            full_name = full_name.strip()
            if " " in full_name:
                instance.first_name, instance.last_name = full_name.split(" ", 1)
            else:
                instance.first_name = full_name
                instance.last_name = ""
            instance.name = full_name

        return super().update(instance, validated_data)
