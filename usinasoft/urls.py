from django.contrib import admin
from django.urls import path, include

# Usar DefaultRouter para expor um root /api/ que lista todas as rotas registradas
from rest_framework.routers import DefaultRouter

# importar viewsets das apps e registrá-los no router raiz
from usuarios.views import UsuarioViewSet, LogAcaoViewSet
from pecas.views import ClienteViewSet, PecaViewSet
from producao.views import OrdemProducaoViewSet, OrdemProducaoItemViewSet
from atividades.views import AtividadeViewSet, ComentarioViewSet, AnexoViewSet

router = DefaultRouter()
router.register(r"usuarios", UsuarioViewSet, basename="usuario")
router.register(r"logs", LogAcaoViewSet, basename="logacao")
router.register(r"clientes", ClienteViewSet, basename="cliente")
router.register(r"pecas", PecaViewSet, basename="peca")
router.register(r"ops", OrdemProducaoViewSet, basename="ordemproducao")
router.register(r"itens-op", OrdemProducaoItemViewSet, basename="ordemproducaoitem")
router.register(r"atividades", AtividadeViewSet, basename="atividade")
router.register(r"comentarios", ComentarioViewSet, basename="comentario")
router.register(r"anexos", AnexoViewSet, basename="anexo")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
