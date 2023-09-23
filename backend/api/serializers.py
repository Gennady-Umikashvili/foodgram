from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.db.models import F

from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField

from .models import (
    Ingredient,
    Recipe,
    Tag,
    UserCart,
    User,
    Follow,
    Favorite,
    Amount,
)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class CurrentUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        current_user = self.context.get("request").user
        return current_user.is_authenticated and Follow.objects.filter(
            user=current_user, author=obj).exists()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )


class TinyRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = Amount
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    author = CurrentUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipe_amounts"
    )

    def get_is_favorited(self, obj):
        current_user = self.context.get("request").user
        return current_user.is_authenticated and Favorite.objects.filter(
            user=current_user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context.get("request").user
        return current_user.is_authenticated and UserCart.objects.filter(
            user=current_user, recipe=obj).exists()

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            "id", "name", "measurement_unit", amount=F("ingredients__amount")
        )

    def validate_ingredients(self, ingredients):
        if len(ingredients) == 0:
            raise serializers.ValidationError(
                "ингредиенты не указаны"
            )

        ingredients_in_recipe = []
        for ingredient in ingredients:
            if ingredient["ingredient"]["id"] in ingredients_in_recipe:
                raise serializers.ValidationError(
                    "нужны уникальные ингредиенты"
                )
            ingredients_in_recipe.append(ingredient["ingredient"]["id"])

        return ingredients

    def validate_tags(self, tags):
        if len(tags) == 0:
            raise serializers.ValidationError(
                "теги не указаны"
            )

        tags_in_recipe = []
        for tag in tags:
            if tag.id in tags_in_recipe:
                raise serializers.ValidationError(
                    "нужны уникальные теги"
                )
            tags_in_recipe.append(tag.id)

        return tags

    @staticmethod
    def create_ingredients(ingredients, recipe):
        new_ingredients = []
        for ingredient in ingredients:
            new_ingredients.append(Amount(
                recipe=recipe,
                ingredient_id=ingredient["ingredient"]["id"],
                amount=ingredient["amount"],
            ))
        Amount.objects.bulk_create(new_ingredients)

    @atomic()
    def create(self, context):
        ingredients = context.pop("recipe_amounts")
        tags = context.pop("tags")
        recipe = Recipe.objects.create(**context)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    @atomic()
    def update(self, recipe, data):
        ingredients = data.pop("recipe_amounts")
        tags = data.pop("tags")
        super().update(recipe, data)
        recipe.tags.set(tags)
        recipe.recipe_amounts.all().delete()
        self.create_ingredients(ingredients, recipe)
        return recipe

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class RecipeCreateSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class UserCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCart
        fields = ("user", "recipe")


class FollowSerializer(CurrentUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = request.GET.get("recipes_limit")
        queryset = Recipe.objects.filter(author=obj)
        if recipes_limit:
            queryset = queryset[: int(recipes_limit)]
        return TinyRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class CurrentUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "password",
            "username",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "email": {"required": True},
            "password": {"required": True},
            "username": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }
