from rest_framework.filters import SearchFilter

from django_filters.rest_framework import FilterSet, filters

from .models import Recipe, Tag


class AuthorTagFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        to_field_name="slug",
        field_name="tags__slug",
    )
    favorite = filters.BooleanFilter(method="favorite_filter")
    cart = filters.BooleanFilter(method="cart_filter")

    def favorite_filter(self, queryset, name, value):
        current_user = self.request.user
        if value:
            return queryset.filter(favorite_by_user__user=current_user)
        return queryset


    def cart_filter(self, queryset, name, value):
        current_user = self.request.user
        if value:
            return queryset.filter(in_user_cart__user=current_user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "tags")


class IngredientFilter(SearchFilter):
    search_param = "name"
