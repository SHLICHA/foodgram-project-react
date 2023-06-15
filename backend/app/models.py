from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import UniqueConstraint
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        "Тег",
        max_length=50,
        unique=True
    )
    color = models.CharField(
        "Цвет тега",
        max_length=8,
        null=True,
        unique=True
    )
    slug = models.SlugField(
        max_length=50,
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
        return self.slug


class Ingredient(models.Model):
    name = models.CharField(
        "Название ингридиента",
        max_length=200,
    )
    measurement_unit = models.CharField(
        "Единица измерения",
        max_length=10
    )

    class Meta:
        ordering = ('name',)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        UniqueConstraint(fields=['name', 'measurement_unit'],
                         name='unique_ingredient')

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
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        default=0,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        through='CountIngredients'
    )
    text = models.TextField(
        'Описание рецепта',
        max_length=10000,
        blank=True
    )
    count_add_favorite = models.PositiveIntegerField(
        "Количество добавление в избранное",
        default=0,
        null=True
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class CountIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name='amount_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
        related_name='amount_ingredient'
    )
    amount = models.PositiveIntegerField(
        "Количество ингредиента",
        validators=(MinValueValidator(1),),
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = "Количество ингредиентов"
        verbose_name_plural = "Количество ингредиентов"

    def __str__(self):
        return f'{self.recipe.name} {self.ingredient.name}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        verbose_name='Подписчик',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ('user', 'author',)
        UniqueConstraint(fields=['user', 'author'],
                         name='unique_follow')

    def __str__(self):
        return f'{self.user.username} {self.author.username}'


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorite_user',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        unique_together = ('user', 'recipe',)
        UniqueConstraint(fields=['user', 'recipe'],
                         name='unique_favorite')

    def __str__(self):
        return f'{self.user.username} {self.recipe.name}'


class ShopingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='buyer',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shoping_cart',
        verbose_name='Избранный рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"
    UniqueConstraint(fields=['user', 'recipe'],
                     name='unique_recipe_in_shoping_cart')

    def __str__(self):
        return f'{self.user.username} {self.author.name}'
