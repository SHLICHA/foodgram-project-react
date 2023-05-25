from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from app.models import Ingredient, Tag, Recipe
from users.models import User
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    UserSerializer,
    GetTokenSerializer,
    ChangePasswordSerializer
    )


class UserViewSet(viewsets.ModelViewSet):
    """Работа администратора с данными пользователей.
    Создание, изменение, удаление. Ссылка ../users/{username}/ - страница
    пользователя для работы. На вход приходит username пользователя.
    ../users/ - получение списка пользователей"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    http_method_names = ["get", "post", "patch", "delete"]
    permission_classes = [AllowAny, ]

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.validated_data, status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, pk=None):
        """Получение пользователя"""
        queryset = User.objects.filter(id=pk)
        user = get_object_or_404(queryset)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def destroy(self, request, pk):
        """Удаление пользователя"""
        queryset = User.objects.filter(username=pk)
        user = get_object_or_404(queryset)
        user.delete()
        return Response(
            "Пользователь удален", status=status.HTTP_204_NO_CONTENT
        )

    def partial_update(self, request, pk):
        """Изменение данных пользователя"""
        queryset = User.objects.filter(username=pk)
        user = get_object_or_404(queryset)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(
                "Некорректные данные", status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.validated_data)

    @action(
        methods=["get", "patch"],
        detail=False,
        url_path="me",
    )
    def me(self, request):
        """Получение собственных данных"""
        serializer = UserSerializer(request.user)
        if request.method == "GET":
            return Response(serializer.data)
        else:
            pk = request.user.pk
            user = User.objects.get(id=pk)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(
                    "Некорректные данные", status=status.HTTP_400_BAD_REQUEST
                )
            return Response(serializer.validated_data)

    @action(
        methods=["post"],
        detail=False,
        url_path="set_password",
    )
    def update_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        if serializer.is_valid():
            current_password = serializer.validated_data["current_password"]
            print(current_password)
            if not user.check_password(current_password):
                return Response("Неверный текущий пароль",
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
