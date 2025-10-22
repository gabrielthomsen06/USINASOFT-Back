from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import OrdemProducaoViewSet, OrdemProducaoItemViewSet, indicadores_summary

router = DefaultRouter()
router.register(r"ops", OrdemProducaoViewSet, basename="ordemproducao")
router.register(r"itens-op", OrdemProducaoItemViewSet, basename="ordemproducaoitem")

urlpatterns = [
    # Endpoint de indicadores (agregação em tempo real)
    path("indicadores/summary/", indicadores_summary, name="indicadores-summary"),
] + router.urls
