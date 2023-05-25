from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register(r"ingredients/(?P<ingredient_id>\d+)",
                IngredientViewSet,
                basename="ingredient"
                )
router.register('tags', TagViewSet, basename='tags')
router.register(r"tags/(?P<tag_id>\d+)",
                TagViewSet,
                basename="tag"
                )
router.register('users', UserViewSet, basename="users")
router.register(r"users/(?P<user_id>\d+)",
                UserViewSet,
                basename="user"
                )
router.register('recipes', RecipeViewSet, basename="recipes")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include('djoser.urls.authtoken'))
]
