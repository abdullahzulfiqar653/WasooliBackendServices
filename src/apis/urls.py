from django.urls import path, include
from apis.views import (
    OTPView,
    LookupListAPIView,
    MemberRetrieveByPhoneAPIView,
    MerchantMemberListCreateAPIView,
    MemberRetrieveUpdateDestroyAPIView,
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
        "merchants/<str:merchant_id>/members/",
        MerchantMemberListCreateAPIView.as_view(),
        name="merchant-members-list-create",
    ),
    path(
        "merchants/<str:merchant_id>/members/<str:phone>/",
        MemberRetrieveByPhoneAPIView.as_view(),
        name="merchant-member-retrieve",
    ),
    # =====================================================
    # MerchantMember
    # =====================================================
    path(
        "members/<str:pk>/",
        MemberRetrieveUpdateDestroyAPIView.as_view(),
        name="member-retrieve-update-destroy",
    ),
    # =====================================================
    # Lookups
    # =====================================================
    path("lookup/<str:flag>/", LookupListAPIView.as_view(), name="lookup-list"),
]
