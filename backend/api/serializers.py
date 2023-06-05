import base64

from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from django.core.validators import MaxLengthValidator, RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from app.models import (
    CountIngredients,
    Favorites,
    Follow,
    Ingredient,
    Recipe,
    ShopingCart,
    Tag
)
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag
        extra_kwargs = {
            'name': {'read_only': True},
            'color': {'read_only': True},
            'slug': {'read_only': True},
        }


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


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
        extra_kwargs = {
            'name': {'read_only': True},
            'measurement_unit': {'read_only': True},
        }


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message="Некорректный логин",
            ),
            MaxLengthValidator(150, "Логин слишком длинный"),
            UniqueValidator(queryset=User.objects.all()),
        ],
        required=True
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(254, "Адрес слишком длинный"),
        ],
        required=True
    )
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def create(self, validated_data):

        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get(
            "first_name", instance.first_name
        )
        instance.last_name = validated_data.get(
            "last_name", instance.last_name
        )
        instance.save()
        return instance

    def validate(self, data):
        if data.get("username") == "me":
            raise serializers.ValidationError("Запрещенный логин")
        if User.objects.filter(username=data.get("username")):
            raise serializers.ValidationError(
                "Пользователь с таким username уже существует"
            )
        if User.objects.filter(email=data.get("email")):
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует"
            )
        return data

    def validate_email(self, value):
        norm_email = value.lower()
        if User.objects.filter(email=norm_email).exists():
            raise serializers.ValidationError("Not unique email")
        return norm_email

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_is_subscribed(self, obj):
        request = self.context.get('request', None)
        if request:
            current_user = request.user
            if current_user.is_authenticated:
                return current_user.follower.filter(author=obj).exists()
        return False


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=True)
    author = UserSerializer(read_only=True)
    ingredients = CountIngredientsSerializer(
        many=True,
        source='amount_ingredient',
        required=True
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
        try:
            tags = Tag.objects.filter(pk__in=tags_pk)
        except Tag.DoesNotExist:
            raise ValidationError(
                {'tags': ['Переданы несужествующие теги']},
                code='invalid',
            )
        internal_data['tags'] = tags
        return internal_data

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
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['id']
            amount = ingredient_data['amount']
            CountIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
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
        for ingredien_data in ingredients_data:
            recipe = Recipe.objects.get(pk=instance.id)
            CountIngredients.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredien_data['id'],
                amount=ingredien_data['amount']
            )
        return instance

    def get_is_favorited(self, obj):
        request = self.context["request"]
        user = request.user
        if user.is_authenticated:
            if Favorites.objects.filter(recipe=obj,
                                        user=user
                                        ).exists():
                return True
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context["request"]
        user = request.user
        if user.is_authenticated:
            if ShopingCart.objects.filter(
                recipe=obj,
                user=user
            ).exists():
                return True
        return False


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password',)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UserSerializer):
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count'
                  )

    def validate(self, author, *args, **kwargs):
        user = self.context["request"].user
        author = self.context["author"]
        if user == author:
            raise serializers.ValidationError('Подписка на самого себя!')
        if Follow.objects.filter(user=user,
                                 author=author
                                 ).exists():
            raise serializers.ValidationError('Вы уже подписаны')
        return author

    def get_recipes(self, obj):
        return RecipeMinifiedSerializer(
            Recipe.objects.filter(author=obj),
            many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
