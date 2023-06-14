from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.models import CountIngredients, Ingredient, Recipe, Tag
from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class CountIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = CountIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=True)
    author = UserSerializer(read_only=True)
    ingredients = CountIngredientsSerializer(
        many=True,
        source='amount_ingredient',
    )
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField(
        read_only=True,
        default=False)
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True,
        default=False)

    def to_internal_value(self, data):
        tags_pk = data.get('tags')
        internal_data = super().to_internal_value(data)
        tags = []
        try:
            for tag in tags_pk:
                tags.append(Tag.objects.get(pk=tag))
        except TypeError:
            raise serializers.ValidationError(
                {'tags': ['Добавьте теги']},
                code='invalid',
            )
        except Tag.DoesNotExist:
            raise ValidationError(
                {'tags': ['Переданы несуществующие теги']},
                code='invalid',
            )
        internal_data['tags'] = tags
        return internal_data

    def validate(self, data):
        errors = []
        tags_pk = data.get('tags')
        if "cooking_time" not in data:
            errors.append('Добавьте время приготовления')
        if data["cooking_time"] <= 0:
            errors.append('Должно быть положительным числом')
        if tags_pk == []:
            errors.append('Добавьте теги')
        elif len(tags_pk) != len(set(tags_pk)):
            errors.append('Теги не уникальны')
        if errors:
            raise serializers.ValidationError(errors)
        return data

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError('Добавьте ингредиенты')
        for ingredient in value:
            if ingredient.get('amount') <= 0:
                raise ValidationError(
                    f'Добавьте количество ингредиента {ingredient}'
                )
        ingredient_list = [
            inrgedient['id'] for inrgedient in value
        ]
        unique_ingredient_list = set(ingredient_list)
        if len(ingredient_list) != len(unique_ingredient_list):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными'
            )
        return value

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time',
                  )
        extra_kwargs = {
            'author': {'read_only': True},
        }

    def create(self, validated_data):
        ingredients_data = validated_data.pop('amount_ingredient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        objs = [
            CountIngredients(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]
        CountIngredients.objects.bulk_create(objs)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)
        instance.save()
        CountIngredients.objects.filter(recipe_id=instance.id).delete()
        ingredients_data = validated_data.pop('amount_ingredient')
        recipe = Recipe.objects.get(pk=instance.id)
        CountIngredients.objects.filter(recipe=recipe).delete()
        objs = [
            CountIngredients(
                recipe=recipe,
                ingredient=ingredien_data['id'],
                amount=ingredien_data['amount']
            )
            for ingredien_data in ingredients_data
        ]
        CountIngredients.objects.bulk_create(objs)
        return instance

    def get_is_favorited(self, obj):
        request = self.context["request"]
        user = request.user
        if (user.is_authenticated
           and user.favorite_user.filter(recipe=obj).exists()):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context["request"]
        user = request.user
        if (user.is_authenticated
           and user.buyer.filter(recipe=obj).exists()):
            return True
        return False


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = Base64ImageField(allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
