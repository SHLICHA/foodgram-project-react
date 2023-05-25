import base64

from django.core.files.base import ContentFile
from django.core.validators import RegexValidator, MaxLengthValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from app.models import Ingredient, Tag, Recipe, CountIngredients
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CountIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
        )

    class Meta:
        model = CountIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


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

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
            )
        extra_kwargs = {
            'password': {'write_only': True}
        }


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    ingredients = CountIngredientsSerializer(read_only=True, many=True)
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'image', 'text', 'cooking_time', 'name')
        read_only_fields = ('author',)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(**ingredient)
            CountIngredients.objects.create(
                recipe=recipe,
                ingredient=current_ingredient.pk,
                amount=ingredient['amount']
            )


class GetTokenSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            MaxLengthValidator(254, "Адрес слишком длинный"),
        ]
    )

    def validate(self, data):
        errors = []
        if "email" not in data:
            errors.append("Введите email")
        if "password" not in data:
            errors.append("Введите пароль")
        if not User.objects.filter(username=data.get("email")).exists():
            errors.append("Несуществующий пользователь")
        return data

    class Meta:
        model = User
        fields = (
            "email",
            "password",
        )


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password',)

    def validate_new_password(self, value):
        validate_password(value)
        return value
