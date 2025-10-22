from rest_framework.routers import DefaultRouter
from .views import AtividadeViewSet, ComentarioViewSet, AnexoViewSet

router = DefaultRouter()
router.register(r"atividades", AtividadeViewSet, basename="atividade")
router.register(r"comentarios", ComentarioViewSet, basename="comentario")
router.register(r"anexos", AnexoViewSet, basename="anexo")

urlpatterns = router.urls
