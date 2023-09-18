from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "api"

router = DefaultRouter()
router.register("recipes", views.RecipeViewSet)
router.register("tags", views.TagsViewSet)
router.register("ingredients", views.IngredientsViewSet)
router.register("users", views.CurrentUserViewSet)

urlpatterns = [
    path("import_data/", views.import_data, name="import_data"),
    path("", include(router.urls)),
]
