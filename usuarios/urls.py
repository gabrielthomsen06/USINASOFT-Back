from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, LogAcaoViewSet, current_user

router = DefaultRouter()
router.register(r"usuarios", UsuarioViewSet, basename="usuario")
router.register(r"logs", LogAcaoViewSet, basename="logacao")

urlpatterns = [
    path("auth/me/", current_user, name="current-user"),
] + router.urls
