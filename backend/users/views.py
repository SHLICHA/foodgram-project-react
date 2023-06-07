from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from app.models import Follow

from .serializers import (ChangePasswordSerializer, FollowSerializer,
                          UserSerializer)

User = get_user_model()


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

    @action(
        methods=["get", "patch"],
        detail=False,
        url_path="me",
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        """Получение собственных данных"""
        serializer = UserSerializer(request.user)
        if request.method == "GET":
            return Response(serializer.data)
        pk = request.user.pk
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                "Некорректные данные", status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(serializer.validated_data)

    @action(
        methods=["post"],
        detail=False,
        url_path="set_password",
        permission_classes=[IsAuthenticated, ]
    )
    def update_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        if serializer.is_valid():
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['post', 'delete'],
            url_path=r'(?P<id>\d+)/subscribe',
            permission_classes=(IsAuthenticated,)
            )
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(User, pk=kwargs.get('id'))
        user = self.request.user
        if request.method == "POST":
            serializer = FollowSerializer(
                author,
                data=request.data,
                context={'request': request, 'author': author})
            if serializer.is_valid(raise_exception=True):
                Follow.objects.get_or_create(
                    user=user,
                    author=author
                )
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        user.follower.filter(
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            url_path='subscriptions',
            permission_classes=(IsAuthenticated,)
            )
    def subscriptions(self, request):
        user = self.request.user
        followings = Follow.objects.filter(user=user)
        query_author = [i.author for i in followings]
        queryset = User.objects.filter(username__in=query_author)
        recipes_limit = self.request.query_params.get('recipes_limit')
        if recipes_limit:
            queryset = queryset.filter(recipe_count__lte=recipes_limit)
        serializer = FollowSerializer(queryset, many=True)
        return Response(serializer.data)
