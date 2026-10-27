from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True, default="")
    medical_history = serializers.CharField(required=False, allow_blank=True, default="")
    contact_number = serializers.CharField(required=False, allow_blank=True, default="")
    created_by_user = serializers.ReadOnlyField(source="created_by.email")

    class Meta:
        model = Patient
        fields = [
            "id",
            "name",
            "first_name",
            "last_name",
            "age",
            "gender",
            "address",
            "medical_history",
            "contact_number",
            "email",
            "created_by_user",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by_user", "created_at", "updated_at"]

    def to_internal_value(self, data):
        # Create a mutable copy if necessary
        mutable_data = data.copy() if hasattr(data, "copy") else dict(data)

        # Normalize gender if provided
        if "gender" in mutable_data and mutable_data["gender"] is not None:
            raw_gender = str(mutable_data["gender"]).strip().lower()
            if raw_gender in {"m", "male"}:
                mutable_data["gender"] = "male"
            elif raw_gender in {"f", "female"}:
                mutable_data["gender"] = "female"
            elif raw_gender in {"o", "other"}:
                mutable_data["gender"] = "other"
            else:
                raise serializers.ValidationError({"gender": 'Gender must be one of: "male", "female", "other".'})

        return super().to_internal_value(mutable_data)

    def validate_age(self, value):
        if value <= 0:
            raise serializers.ValidationError("Age must be a positive integer.")
        if value > 130:
            raise serializers.ValidationError("Age seems unrealistic.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)

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

        return Patient.objects.create(created_by=user, **validated_data)

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
