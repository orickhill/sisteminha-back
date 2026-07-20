from rest_framework import viewsets
from .models import (
    Desenvolvedor,
    Microempreendedor,
    Avaliacao_Desenvolvedor,
    Avaliacao_Sistema,
    Categoria,
    Sistema,
    User,
)
from .serializers import (
    UserSerializer,
    DesenvolvedorSerializer,
    MicroempreendedorSerializer,
    Avaliacao_DesenvolvedorSerializer,
    Avaliacao_SistemaSerializer,
    CategoriaSerializer,
    SistemaSerializer,
)
from .filters import DesenvolvedorFilter, SistemaFilter
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404

## Permissions
from rest_framework.permissions import IsAuthenticated

from rest_framework import status


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = (MultiPartParser, FormParser)


class DesenvolvedorViewSet(viewsets.ModelViewSet):
    queryset = Desenvolvedor.objects.all()
    serializer_class = DesenvolvedorSerializer
    parser_classes = (MultiPartParser, FormParser)
    filterset_class = DesenvolvedorFilter
    search_fields = ["user__first_name"]
    ordering_fields = ["user__first_name"]

    @action(detail=True, methods=["get"])
    def avaliacoes_desenvolvedor(self, request, pk):
        desenvolvedor_id = pk
        avaliacoes = Avaliacao_Desenvolvedor.objects.filter(
            desenvolvedor=desenvolvedor_id
        )
        serializer = Avaliacao_DesenvolvedorSerializer(avaliacoes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def sistemas_desenvolvedor(self, request, pk):
        desenvolvedor_id = pk
        sistemas = Sistema.objects.filter(desenvolvedor=desenvolvedor_id)
        serializer = SistemaSerializer(sistemas, many=True)
        return Response(serializer.data)


class MicroempreendedorViewSet(viewsets.ModelViewSet):
    queryset = Microempreendedor.objects.all()
    serializer_class = MicroempreendedorSerializer
    parser_classes = (MultiPartParser, FormParser)


class Avaliacao_DesenvolvedorViewSet(viewsets.ModelViewSet):
    queryset = Avaliacao_Desenvolvedor.objects.all()
    serializer_class = Avaliacao_DesenvolvedorSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)


class Avaliacao_SistemaViewSet(viewsets.ModelViewSet):
    queryset = Avaliacao_Sistema.objects.all()
    serializer_class = Avaliacao_SistemaSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    parser_classes = (MultiPartParser, FormParser)


class SistemaViewSet(viewsets.ModelViewSet):
    queryset = Sistema.objects.all()
    serializer_class = SistemaSerializer
    parser_classes = (MultiPartParser, FormParser)
    filterset_class = SistemaFilter
    search_fields = ["nome"]
    ordering_fields = ["nome"]

    @action(detail=True, methods=["get"])
    def sistemas_por_categoria(self, request, pk):
        categoria_id = pk
        sistemas = Sistema.objects.filter(categoria=categoria_id)
        serializer = SistemaSerializer(sistemas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def avaliacoes_sistema(self, request, pk):
        sistema_id = pk
        avaliacoes = Avaliacao_Sistema.objects.filter(desenvolvedor=sistema_id)
        serializer = Avaliacao_SistemaSerializer(avaliacoes, many=True)
        return Response(serializer.data)


## AUTENTICAÇÃO


class DesenvolvedorRegistrationView(APIView):
    def post(self, request):
        user_data = request.data.get("user")  ## Pega os dados do user da requisição
        cpf = request.data.get("cpf")
        github = request.data.get("github")

        try:
            user_serializer = UserSerializer(data=user_data)
            if user_serializer.is_valid():  # Verifica se os dados do user são válidos
                cpfAlreadyExists = Desenvolvedor.objects.filter(cpf=cpf)
                if not(cpfAlreadyExists):
                    user = user_serializer.save()
                else:
                    return Response(
                        {"cpf": "Desenvolvedor with this cpf already exists"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    user_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
            desenvolvedor_data = {
                "user": user.id,  # Passar o ID do user
                "cpf": cpf,
                "github": github,
            }
            desenvolvedor_serializer = DesenvolvedorSerializer(data=desenvolvedor_data)
            if desenvolvedor_serializer.is_valid():
                desenvolvedor = desenvolvedor_serializer.save()
                desenvolvedor_serializer = DesenvolvedorSerializer(desenvolvedor)
                return Response(
                    desenvolvedor_serializer.data, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    desenvolvedor_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {"error": "Server error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DesenvolvedorLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        # user_request = User.objects.get(email=email)
        user_request = get_object_or_404(User, email=email)

        if user_request is not None:
            username = user_request.username
            password = request.data.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                if created:
                    token.delete()  # Deleta o token antigo
                    token = Token.objects.create(user=user)

                response_data = {
                    "token": token.key,
                    "username": user.username,
                    "perfil": user.perfil,
                }

                if user.perfil == "desenvolvedor":
                    desenvolvedor = (
                        user.desenvolvedor
                    )  # Assumindo que a relação tem nome "desenvolvedor"
                    if desenvolvedor is not None:
                        # Adiciona os dados do desenvolvedor ao response_data
                        desenvolvedor_data = DesenvolvedorSerializer(desenvolvedor).data
                        response_data["data"] = desenvolvedor_data

                return Response(response_data)
            else:
                return Response(
                    {"message": "Usuário ou Senha Inválido"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        else:
            return Response(
                {"message": "Usuário ou Senha Inválido"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class MicroempreendedorRegistrationView(APIView):
    def post(self, request):
        user_data = request.data.get("user")  ## Pega os dados do user da requisição
        cnpj = request.data.get("cnpj")

        try:
            user_serializer = UserSerializer(data=user_data)
            if user_serializer.is_valid():
                user = user_serializer.save()
            else:
                return Response(
                    user_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
            microempreendedor_data = {
                "user": user.id,  # Passar o ID do user
                "cnpj": cnpj,
            }
            microempreendedor_serializer = MicroempreendedorSerializer(
                data=microempreendedor_data
            )
            if microempreendedor_serializer.is_valid():
                microempreendedor = microempreendedor_serializer.save()
                microempreendedor_serializer = MicroempreendedorSerializer(
                    microempreendedor
                )
                return Response(
                    microempreendedor_serializer.data, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    microempreendedor_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {"error": "Server error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MicroempreendedorLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        user_request = User.objects.get(email=email)

        if user_request is not None:
            username = user_request.username
            password = request.data.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                if created:
                    token.delete()
                    token = Token.objects.create(user=user)

                response_data = {
                    "token": token.key,
                    "username": user.username,
                    "perfil": user.perfil,
                }

                if user.perfil == "microempreendedor":
                    microempreendedor = user.microempreendedor
                    if microempreendedor is not None:
                        microempreendedor_data = MicroempreendedorSerializer(
                            microempreendedor
                        ).data
                        response_data["data"] = microempreendedor_data

                return Response(response_data)
            else:
                return Response(
                    {"message": "Usuário ou Senha Inválido"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        else:
            return Response(
                {"message": "Usuário ou Senha Inválido"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class RegistroUsuarioView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUsuarioView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            token, created = Token.objects.get_or_create(user=usuario)
            if created:
                token.delete()
                token = Token.objects.create(user=usuario)
            return Response(
                {
                    "token": token.key,
                    "username": usuario.username,
                    "perfil": usuario.perfil,
                }
            )
        else:
            return Response(
                {"mensagem": "Login ou Senha Inválido"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.headers)
        token_key = request.auth.key
        token = Token.objects.get(key=token_key)
        token.delete()

        return Response({"detail": "Usuário deslogado com sucesso."})
