from django.contrib import admin

from .models import (CountIngredients, Favorites, Follow, Ingredient, Recipe,
                     ShopingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)


class CountIngredientsAdmin(admin.TabularInline):
    model = CountIngredients


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'pub_date')
    inlines = (CountIngredientsAdmin,)
    search_fields = ('name', 'author', 'tags')
    list_filter = ('author', 'tags',)
    empty_value_display = '-пусто-'


admin.site.register(Tag)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    list_filter = ('user', 'author',)


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    list_filter = ('user',)


@admin.register(ShopingCart)
class ShopingCart(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    list_filter = ('user',)
