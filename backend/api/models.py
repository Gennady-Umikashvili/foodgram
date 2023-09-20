from colorfield.fields import ColorField
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        "email",
        unique=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = (
        "first_name",
        "last_name",
        "password",
        "username",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email[:15]


class Ingredient(models.Model):
    name = models.CharField(
        "Ингредиент",
        max_length=200
    )
    measurement_unit = models.CharField(
        "Единица измерения",
        max_length=200
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient",
            )
        ]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name", "measurement_unit")

    def __str__(self):
        return self.name[:15]


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="recipes"
    )
    name = models.CharField(
        "Название рецепта",
        max_length=200
    )
    image = models.ImageField(
        verbose_name="Картинка",
        upload_to="recipes/"
    )
    text = models.TextField("Рецепт")
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        through="Amount"
    )
    tags = models.ManyToManyField(
        "Tag",
        verbose_name="Теги"
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления в минутах",
        validators=(
            MaxValueValidator(
                240,
                message="Максимальное время 240 мин"),
            MinValueValidator(
                1,
                message="Минимальное время 1 мин",)
            ),
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("name", "cooking_time")

    def __str__(self):
        return self.name[:15]


class Amount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="Ингредиент",
        on_delete=models.PROTECT,
        related_name="ingredients"
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="recipe_amounts"
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        validators=(
            MaxValueValidator(
                240,
                message="Максимальное количество ингредиентов 20"
            ),
            MinValueValidator(
                1,
                message="Минимальное количество ингредиентов 1"
            ),
        )
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ingredient", "recipe"],
                name="unique_ingredient_in_recipe",
            )
        ]
        verbose_name = "Количество ингредиента"
        verbose_name_plural = "Количество ингредиентов"
        ordering = ("recipe", "ingredient")

    def __str__(self):
        return (f"{self.recipe} - {self.ingredient.name} {self.amount} "
                f"{self.ingredient.name}")


class Tag(models.Model):
    name = models.CharField(verbose_name="Тег", max_length=200, unique=True)
    color = ColorField(verbose_name="Цвет", format="hex", unique=True)
    slug = models.SlugField(verbose_name="slug", max_length=200, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        return self.name[:10]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="favorite_recipes",
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="favorite_by_user",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_recipe_for_user",
            )
        ]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        ordering = ("user", "recipe")

    def __str__(self):
        return self.recipe[:15]


class UserCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="recipes_in_cart",
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="in_user_cart",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_recipe_for_user_in_cart",
            )
        ]
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"
        ordering = ("user", "recipe")

    def __str__(self):
        return self.recipe.name[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="author",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_following",
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="is_not_following",
            ),
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ("author", "user")

    def __str__(self):
        return f'{self.user} {self.author}'
