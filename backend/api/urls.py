from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register("recipes", views.RecipeViewSet)
router.register("tags", views.TagsViewSet)
router.register("ingredients", views.IngredientsViewSet)
router.register("users", views.CurrentUserViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
