from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    email = models.EmailField("email", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "password", "username"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Ingredient(models.Model):
    name = models.CharField(verbose_name="Ингредиент", max_length=200)
    measurement_unit = models.CharField(
        verbose_name="Единица измерения", max_length=200
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"], name="unique_ingredient"
            )
        ]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name", "measurement_unit")

    def __str__(self):
        return self.name.title()


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="recipes",
        verbose_name="Автор",
        null=True,
    )
    name = models.CharField(verbose_name="Название рецепта", max_length=200)
    image = models.ImageField(upload_to="recipes/", verbose_name="Картинка")
    text = models.TextField(verbose_name="Рецепт")
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name="Ингредиенты", through="Amount"
    )
    tags = models.ManyToManyField("Tag", verbose_name="Теги")
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления в минутах",
        validators=(MinValueValidator(1),),
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("name", "cooking_time")

    def __str__(self):
        return self.name


class Amount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name="ingredients",
        verbose_name="Ингредиент",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_amounts",
        verbose_name="Рецепт",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество", validators=(MinValueValidator(1),)
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
        return "{1} - {0} {2} ({3})".format(
            self.ingredient, self.recipe, self.amount, self.ingredient.unit
        )


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Тег")
    color = models.CharField(max_length=200, unique=True, verbose_name="Цвет")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="slug")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_recipes",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite_by_user",
        verbose_name="Рецепт",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_recipe_for_user"
            )
        ]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        ordering = ("user", "recipe")

    def __str__(self):
        return self.recipe


class UserCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes_in_cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_user_cart",
        verbose_name="Рецепт",
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
        return self.recipe


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Пользователь",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="author",
        verbose_name="Автор",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_following"
            )
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ("author", "user")

    def __str__(self):
        return self.user + " " + self.author
