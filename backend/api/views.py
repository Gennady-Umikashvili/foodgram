<<<<<<< HEAD
=======
from django.shortcuts import render
>>>>>>> 4d80f233 (fix)
import json
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from djoser.views import UserViewSet

from .models import (
    Ingredient,
    Recipe,
    Tag,
    Favorite,
    UserCart,
    Amount,
    User,
    Follow,
)
from .serializers import (
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    TinyRecipeSerializer,
    FollowSerializer,
    RecipeCreateSerializer,
)
<<<<<<< HEAD
from .permissions import OwnerOrRO
=======
from .permissions import OwnerOrRO, AdminOrRO
>>>>>>> 4d80f233 (fix)
from .filters import AuthorTagFilter, IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    pagination_class = PageNumberPagination
    permission_classes = [OwnerOrRO]
    filterset_class = AuthorTagFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return RecipeSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        if self.request.query_params.get("is_favorited") == "1":
            self.queryset = self.queryset.filter(
                favorite_by_user__user=self.request.user
            )
        if self.request.query_params.get("is_in_shopping_cart") == "1":
            self.queryset = self.queryset.filter(
                in_user_cart__user=self.request.user
            )
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    # def favorite(self, request, pk=None):
    def favorite(self, request, **kwargs):
        pk = kwargs.get("pk")
        if request.method == "POST":
            return self.__add(Favorite, request.user, pk)
        if request.method == "DELETE":
            return self.__delete(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        if request.method == "POST":
            return self.__add(UserCart, request.user, pk)
        if request.method == "DELETE":
            return self.__delete(UserCart, request.user, pk)

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        shopping_list = {}
        ingredients = Amount.objects.filter(
            recipe__in_user_cart__user=request.user
        ).values_list(
            "ingredient__name", "ingredient__measurement_unit", "amount"
        )
        for name, measurement_unit, amount in ingredients:
            if name not in shopping_list:
                shopping_list[(name, measurement_unit)] = amount
            else:
                shopping_list[(name, measurement_unit)] += amount
        pdfmetrics.registerFont(TTFont("Cornerita", "Cornerita.ttf", "UTF-8"))
        response = HttpResponse()
        response["Content-Type"] = "application/pdf"
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopping_list.pdf"'
        shopping_list_pdf = canvas.Canvas(response)
        shopping_list_pdf.setFont("Cornerita", size=18)
        font_size = 12
        line_size = int(font_size * 1.5)
        v_offset = line_size * len(shopping_list) + 600
        shopping_list_pdf.drawString(200, v_offset + 50, "список покупок")
        shopping_list_pdf.setFont("Cornerita", size=font_size)
        line_no = 1
        for name, measurement_unit in sorted(shopping_list.keys()):
            shopping_list_pdf.drawString(
                70,
                v_offset,
                "{}. {} - {} {}".format(
                    line_no,
                    name,
                    shopping_list[(name, measurement_unit)],
                    measurement_unit,
                ),
            )
            line_no += 1
            v_offset -= line_size
        shopping_list_pdf.showPage()
        shopping_list_pdf.save()

        return response

    def __add(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {"errors": "запись уже есть"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe = get_object_or_404(Recipe, pk=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = TinyRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def __delete(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "такой записи нет"}, status=status.HTTP_400_BAD_REQUEST
        )


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [IngredientFilter]
    search_fields = ["^name"]
    pagination_class = None


def import_data(request):
    with open("api/data/ingredients.json") as f:
        data = json.loads(f.read())
    import_count = 0
    imported = []
    for ingredient in data:
        try:
            Ingredient.objects.create(
                name=ingredient["name"],
                measurement_unit=ingredient["measurement_unit"],
            )
            import_count += 1
        except IntegrityError:
            imported.append(ingredient["name"])

    return HttpResponse(
        "Данные по ингридиентам импортированы: {} <br> уже в базе: {}".format(
            import_count, ", ".join(imported)
        )
    )


class CurrentUserViewSet(UserViewSet):
    pagination_class = PageNumberPagination

    @action(detail=True, permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        pass

    @subscribe.mapping.post
    def create_subscribe(self, request, id=None):
        current_user = request.user
        recipe_owner = get_object_or_404(User, pk=id)
        if Follow.objects.filter(
            user=current_user, author=recipe_owner
        ).exists():
            return Response(
                {"errors": "вы уже подписаны"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        following = Follow.objects.create(
            user=current_user, author=recipe_owner
        )
        serializer = FollowSerializer(following, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def del_subscribe(self, request, id=None):
        current_user = request.user
        recipe_owner = get_object_or_404(User, pk=id)
        following = Follow.objects.filter(
            user=current_user, author=recipe_owner
        )
        if not following.exists():
            return Response(
                {"errors": "вы не подписаны"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        following.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        current_user = request.user
        following = Follow.objects.filter(user=current_user)
        pages = self.paginate_queryset(following)
        serializer = FollowSerializer(
            pages, context={"request": request}, many=True
        )
        return self.get_paginated_response(serializer.data)
