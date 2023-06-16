from app.models import (CountIngredients, Favorites, Ingredient, Recipe,
                        ShopingCart, Tag)
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import IngredientFilter
from .permissions import IsUserOwner
from .serializers import (IngredientSerializer, RecipeMinifiedSerializer,
                          RecipeSerializer, TagSerializer)
from .utils import file_creation

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsUserOwner,)
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('author__id', )
    search_fields = ('^name')

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all()
        tags = self.request.query_params.getlist('tags')
        author = self.request.query_params.getlist('author')
        if self.request.query_params.get('is_favorited'):
            queryset = queryset.filter(
                pk__in=Favorites.objects.filter(user=user)
                .values('recipe')
            )
        if self.request.query_params.get('is_in_shopping_cart'):
            queryset = queryset.filter(
                pk__in=ShopingCart.objects.filter(user=user)
                .values('recipe')
            )
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
    def add_favorites(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('id'))
        user = self.request.user
        if request.method == "POST":
            serializer = RecipeMinifiedSerializer(recipe)
            Favorites.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        Favorites.objects.filter(
            user=user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['post', 'delete'],
            url_path=r'(?P<id>\d+)/shopping_cart',
            permission_classes=(IsAuthenticated,)
            )
    def add_shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('id'))
        user = self.request.user
        if request.method == "POST":
            serializer = RecipeMinifiedSerializer(recipe)
            ShopingCart.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        ShopingCart.objects.filter(
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
        shoping_carts = ShopingCart.objects.filter(
            user=request.user
        )
        recipes = [i.recipe.id for i in shoping_carts]
        shoping_list = (CountIngredients.objects.filter(recipe__in=recipes)
                        .order_by('ingredient')
                        .values('ingredient')
                        .annotate(count=Sum("amount"))
                        )
        return file_creation(shoping_list)


@api_view(["GET"])
def get_favorite(request):
    quryset = [i.recipe for i in Favorites.objects.filter(user=request.user)]
    serializer = RecipeMinifiedSerializer(quryset, many=True)
    return Response(serializer.data)
