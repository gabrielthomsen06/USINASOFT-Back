from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, PecaViewSet

router = DefaultRouter()
router.register(r"clientes", ClienteViewSet, basename="cliente")
router.register(r"pecas", PecaViewSet, basename="peca")

urlpatterns = router.urls
