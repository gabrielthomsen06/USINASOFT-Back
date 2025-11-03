from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import OrdemProducaoViewSet, indicadores_summary

router = DefaultRouter()
router.register(r"ops", OrdemProducaoViewSet, basename="ordemproducao")

urlpatterns = [
    # Endpoint de indicadores (agregação em tempo real)
    path("indicadores/summary/", indicadores_summary, name="indicadores-summary"),
] + router.urls
