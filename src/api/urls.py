from django.urls import path, include

urlpatterns = [
    # =====================================================
    # Email
    # =====================================================
    path("auth/", include("rest_framework.urls"))
]
