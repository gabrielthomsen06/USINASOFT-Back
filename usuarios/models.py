import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UsuarioManager(BaseUserManager):
    """Manager customizado para o modelo Usuario."""

    def create_user(self, email, password=None, **extra_fields):
        """Cria e salva um usuário com o email e senha fornecidos."""
        if not email:
            raise ValueError("O email é obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Cria e salva um superusuário."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser deve ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser deve ter is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuário customizado que usa email como identificador único.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nome")
    last_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Sobrenome")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    is_staff = models.BooleanField(default=False, verbose_name="Membro da equipe")
    is_superuser = models.BooleanField(default=False, verbose_name="Superusuário")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Retorna o nome completo do usuário."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    def get_short_name(self):
        """Retorna o nome curto do usuário."""
        return self.first_name or self.email


class LogAcao(models.Model):
    """
    Modelo de auditoria para registrar ações críticas no sistema.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, related_name="logs", verbose_name="Usuário"
    )
    acao = models.CharField(max_length=100, verbose_name="Ação")
    alvo_tipo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tipo do alvo")
    alvo_id = models.UUIDField(blank=True, null=True, verbose_name="ID do alvo")
    detalhes = models.JSONField(blank=True, null=True, verbose_name="Detalhes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Log de Ação"
        verbose_name_plural = "Logs de Ações"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["usuario", "created_at"]),
            models.Index(fields=["acao"]),
            models.Index(fields=["alvo_tipo", "alvo_id"]),
        ]

    def __str__(self):
        return f"{self.acao} - {self.usuario} - {self.created_at}"
