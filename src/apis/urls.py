from django.urls import path, include
from apis.views import TokenCreateView

urlpatterns = [
    # =====================================================
    # Auth
    # =====================================================
    path("auth/", include("rest_framework.urls")),
    path("auth/token/", TokenCreateView.as_view(), name="token-create"),
]
