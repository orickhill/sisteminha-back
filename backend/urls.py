from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from django.conf import settings
from sisteminha.views import (
    UserViewSet,
    DesenvolvedorViewSet,
    MicroempreendedorViewSet,
    Avaliacao_DesenvolvedorViewSet,
    Avaliacao_SistemaViewSet,
    CategoriaViewSet,
    SistemaViewSet,
    RegistroUsuarioView,
    LogoutUsuarioView,
    DesenvolvedorRegistrationView,
    DesenvolvedorLoginView,
    MicroempreendedorRegistrationView,
    MicroempreendedorLoginView,
)


from django.conf.urls.static import static

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Imports explícitos das Views para evitar problemas de importação

# Configuração da documentação Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Documentação da API do Sisteminha",
        default_version="v1",
        description="Documentação da API Sisteminha com Swagger",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="ifrnsisteminha@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Configuração do Router para as Views de API
router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"desenvolvedores", DesenvolvedorViewSet)
router.register(r"microempreendedores", MicroempreendedorViewSet)
router.register(r"avaliacao_Desenvolvedores", Avaliacao_DesenvolvedorViewSet)
router.register(r"avaliacao_Sistemas", Avaliacao_SistemaViewSet)
router.register(r"categorias", CategoriaViewSet)
router.register(r"sistemas", SistemaViewSet)

# Lista de URLs
urlpatterns = [
    # Administração do Django
    path("admin/", admin.site.urls),
    # Rotas da API REST (ViewSets registrados no router)
    path("sisteminha_api/", include(router.urls)),
    # Autenticação com JWT
    path(
        "sisteminha_api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "sisteminha_api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "sisteminha_api/token/verify/", TokenVerifyView.as_view(), name="token_verify"
    ),
    # Endpoints de autenticação personalizados
    path(
        "sisteminha_api/auth/registro/", RegistroUsuarioView.as_view(), name="registro"
    ),
    path("sisteminha_api/auth/logout/", LogoutUsuarioView.as_view(), name="logout"),
    path(
        "sisteminha_api/auth/registro/desenvolvedor/",
        DesenvolvedorRegistrationView.as_view(),
        name="registro-desenvolvedor",
    ),
    path(
        "sisteminha_api/auth/login/desenvolvedor/",
        DesenvolvedorLoginView.as_view(),
        name="login-desenvolvedor",
    ),
    path(
        "sisteminha_api/auth/registro/microempreendedor/",
        MicroempreendedorRegistrationView.as_view(),
        name="registro-microempreendedor",
    ),
    path(
        "sisteminha_api/auth/login/microempreendedor/",
        MicroempreendedorLoginView.as_view(),
        name="login-microempreendedor",
    ),
    # Documentação da API
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # Rota opcional para evitar erro 404 na raiz (`/`)
    path("", lambda request: HttpResponse("API Sisteminha rodando!"), name="home"),
]

# Configuração para servir arquivos de mídia em ambiente de desenvolvimento
# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
