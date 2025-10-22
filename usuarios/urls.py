from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, LogAcaoViewSet

router = DefaultRouter()
router.register(r"usuarios", UsuarioViewSet, basename="usuario")
router.register(r"logs", LogAcaoViewSet, basename="logacao")

urlpatterns = router.urls
