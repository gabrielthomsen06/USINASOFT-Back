from rest_framework import serializers
from .models import Usuario, LogAcao


class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = Usuario
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "full_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "full_name",
            "is_staff",
            "is_superuser",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        # Todo usuário criado via API é admin por padrão
        validated_data.setdefault("is_staff", True)
        validated_data.setdefault("is_superuser", True)
        validated_data.setdefault("is_active", True)

        user = Usuario(**validated_data)
        if password:
            user.set_password(password)
        else:
            # Define uma senha inutilizável se não for fornecida
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class LogAcaoSerializer(serializers.ModelSerializer):
    usuario_email = serializers.ReadOnlyField(source="usuario.email")

    class Meta:
        model = LogAcao
        fields = [
            "id",
            "usuario",
            "usuario_email",
            "acao",
            "alvo_tipo",
            "alvo_id",
            "detalhes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
