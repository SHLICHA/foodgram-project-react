from django.db import models
from django.core.validators import RegexValidator

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        "Тег",
        max_length=200,
        unique=True
    )
    color = models.CharField(
        "Цвет тега",
        max_length=8,
        null=True
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name="slug",
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[-a-zA-Z0-9_]+$",
                message="Слаг тега содержит недопустимый символ",
            )
        ],
    )

    class Meta:
        ordering = ('name',)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        "Название ингридиента",
        max_length=200,
    )
    measurement_unit = models.CharField(
        "Единица измерения",
        max_length=200
    )

    class Meta:
        ordering = ('name',)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Класс рецептов"""

    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта",
        db_index=True,
        unique=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        upload_to='app/images/',
        null=True,
        default=None,
        blank=False
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
    )
    cooking_time = models.IntegerField(
        'Время приготовления в минутах',
        default=0,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        through='CountIngredients'
    )
    text = models.CharField(
        'Описание рецепта',
        max_length=10000,
        blank=True
    )

    count_add_favorite = models.IntegerField(
        "Количество добавление в избранное",
        default=0,
        null=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class CountIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент"
    )
    amount = models.IntegerField(
        "Количество ингредиента",
        default=0,
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = "Количество ингредиентов"
        verbose_name_plural = "Количество ингредиентов"


class IngredientsImport(models.Model):
    """Хранение истории импортов"""
    csv_file = models.FileField(upload_to='uploads/')
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "История загрузки файлов"
        verbose_name_plural = "История загрузки файлов"
