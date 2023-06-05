from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet,
                    get_favorite)

router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register(r"ingredients/(?P<ingredient_id>\d+)",
                IngredientViewSet,
                basename="ingredient"
                )
router.register('tags', TagViewSet, basename='tags')
router.register(r"tags/(?P<tag_id>\d+)",
                TagViewSet,
                basename="tags"
                )
router.register('users', UserViewSet, basename="users")
router.register('recipes', RecipeViewSet, basename="recipes")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include('djoser.urls.authtoken')),
    path("favorites/", get_favorite),
]
