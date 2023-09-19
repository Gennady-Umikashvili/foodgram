from django.contrib import admin

from .models import Ingredient, Recipe, Amount, Tag, Favorite, UserCart, User


admin.site.register(Amount)
admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(UserCart)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "count_favorites")
    list_filter = ("author", "name", "tags")

    def count_favorites(self, recipe):
        return recipe.favorite_by_user.count()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ("username", "email")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_filter = ("name",)
