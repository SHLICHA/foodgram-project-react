from app.models import Follow, Recipe
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MaxLengthValidator, RegexValidator
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message="Некорректный логин",
            ),
            MaxLengthValidator(150, "Логин слишком длинный"),
        ],
        required=True
    )
    email = serializers.EmailField(
        validators=[
            MaxLengthValidator(254, "Адрес слишком длинный"),
        ],
        required=True
    )
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def validate(self, data):
        data['email'] = data['email'].lower()
        if data.get("username").lower() == "me":
            raise serializers.ValidationError("Запрещенный логин")
        if User.objects.filter(username=data.get("username").lower()):
            raise serializers.ValidationError(
                "Пользователь с таким username уже существует"
            )
        if User.objects.filter(email=data.get("email")):
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует"
            )
        return data

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
        request = self.context.get('request')
        if request:
            current_user = request.user
            if current_user.is_authenticated:
                return current_user.follower.filter(author=obj).exists()
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

    def validate(self, data):
        request = self.context["request"]
        user = request.user
        current_password = data.get('current_password')
        if not user.check_password(current_password):
            raise serializers.ValidationError(
                "Неверный текущий пароль"
            )
        return data


class FollowSerializer(UserSerializer):
    email = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()
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
        from api.serializers import RecipeMinifiedSerializer
        return RecipeMinifiedSerializer(
            Recipe.objects.filter(author=obj),
            many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
