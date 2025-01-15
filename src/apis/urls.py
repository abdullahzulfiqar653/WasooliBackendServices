from django.urls import path, include
from apis.views import (
    OTPView,
    LookupListAPIView,
    MerchantMemberListCreateAPIView,
)


urlpatterns = [
    # =====================================================
    # Auth
    # =====================================================
    path("auth/", include("rest_framework.urls")),
    path("auth/token/", OTPView.as_view(), name="token_obtain_pair"),
    # =====================================================
    # Merchant
    # =====================================================
    path(
        "merchants/<str:merchant_id>/merchant-member/",
        MerchantMemberListCreateAPIView.as_view(),
        name="merchant-member-list-create",
    ),
    # =====================================================
    # Lookups
    # =====================================================
    path("lookup/<str:flag>/", LookupListAPIView.as_view(), name="lookup-list"),
]
