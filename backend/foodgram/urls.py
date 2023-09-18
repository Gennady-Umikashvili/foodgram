from django.contrib import admin
from django.urls import path, include

from djoser.views import TokenCreateView, TokenDestroyView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("api/auth/token/login/", TokenCreateView.as_view()),
    path("api/auth/token/logout/", TokenDestroyView.as_view()),
    path("api/auth/", include("djoser.urls")),
]
