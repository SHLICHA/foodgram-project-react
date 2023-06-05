from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from app.models import (CountIngredients, Favorites, Follow, Ingredient,
                        Recipe, ShopingCart, Tag)

from .permissions import IsUserOwner
from .serializers import (ChangePasswordSerializer, FollowSerializer,
                          IngredientSerializer, RecipeMinifiedSerializer,
                          RecipeSerializer, TagSerializer, UserSerializer)

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
        permission_classes=[IsAuthenticated, ]
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
        Follow.objects.filter(
            user=user,
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
            print(queryset)
        serializer = FollowSerializer(queryset, many=True)
        return Response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (IsUserOwner, )
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('author__id', )
    search_fields = ('^name')

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all()
        tags = self.request.query_params.getlist('tags')
        author = self.request.query_params.getlist('author')
        if self.request.query_params is not None:
            if self.request.query_params.get('is_favorited') == '1':
                temp_queryset = [i.recipe for i in Favorites.objects.filter(
                    user=user
                )]
                queryset = queryset.filter(name__in=temp_queryset)
            if self.request.query_params.get('is_in_shoping_cart') == '1':
                temp_queryset = [i.recipe for i in ShopingCart.objects.filter(
                    user=user
                )]
                queryset = queryset.filter(name__in=temp_queryset)
            if tags:
                queryset = queryset.filter(tags__slug__in=tags)
            if author:
                queryset = queryset.filter(author__pk__in=author)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)
        user.recipe_count = Recipe.objects.filter(author=user).count()
        user.save()

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False,
            methods=['post', 'delete'],
            url_path=r'(?P<id>\d+)/favorite',
            permission_classes=(IsAuthenticated,)
            )
    def subscribe(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('id'))
        user = self.request.user
        if request.method == "POST":
            Favorites.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            serializer = RecipeMinifiedSerializer(recipe, data=request.data)
            if serializer.is_valid(raise_exception=True):
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        Favorites.objects.filter(
            user=user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,)
            )
    def getfile(self, request):
        file_name = open("example.txt", "w+")
        shoping_carts = ShopingCart.objects.filter(
            user=request.user
        )
        recipes = [i.recipe.id for i in shoping_carts]
        shoping_list = (CountIngredients.objects.filter(recipe__in=recipes)
                        .values('ingredient')
                        .annotate(count=Sum("amount")))
        for line_list in shoping_list:
            ingredient = Ingredient.objects.get(pk=line_list['ingredient'])
            file_name.write(f'{ingredient.name} '
                            f'({ingredient.measurement_unit})'
                            f' - {line_list["count"]}\n')
        file_name.close()
        read_file = open("example.txt", "r")
        response = HttpResponse(read_file.read(),
                                content_type="text/plain,charset=utf8"
                                )
        read_file.close()
        message = 'attachment; filename="{}.txt"'.format('file_name')
        response['Content-Disposition'] = message
        return response


@api_view(["GET"])
def get_favorite(request):
    quryset = [i.recipe for i in Favorites.objects.filter(user=request.user)]
    serializer = RecipeMinifiedSerializer(quryset, many=True)
    return Response(serializer.data)
