from django.urls import path, include
from apis.views import (
    OTPView,
    LookupListAPIView,
    RefreshTokenAPIView,
    AccessInfoRetrieveAPIView,
    PreSignedUrlCreateAPIView,
    MemberRetrieveByPhoneAPIView,
    InvoiceRetrieveUpdateAPIView,
    MemberProfileRetrieveAPIView,
    MemberInvoiceListCreateAPIView,
    MerchantMemberListCreateAPIView,
    MerchantDashboardRetrieveAPIView,
    MemberRetrieveUpdateDestroyAPIView,
    MemberSupplyRecordListCreateAPIView,
)


urlpatterns = [
    # =====================================================
    # Auth
    # =====================================================
    path("auth/", include("rest_framework.urls")),
    path("auth/token/", OTPView.as_view(), name="token_obtain_pair"),
    path(
        "auth/access-info/", AccessInfoRetrieveAPIView.as_view(), name="profile_token"
    ),
    path(
        "auth/presigned-url/", PreSignedUrlCreateAPIView.as_view(), name="presigned-url"
    ),
    path("auth/refresh-token/", RefreshTokenAPIView.as_view(), name="refresh_token"),
    # =====================================================
    # Merchant
    # =====================================================
    path(
        "merchants/<str:merchant_id>/dashboard/",
        MerchantDashboardRetrieveAPIView.as_view(),
        name="merchant-dashboard-retrieve",
    ),
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
    path(
        "members/<str:member_id>/invoices/",
        MemberInvoiceListCreateAPIView.as_view(),
        name="member-invoice-list-create",
    ),
    path(
        "members/<str:member_id>/supply-record/",
        MemberSupplyRecordListCreateAPIView.as_view(),
        name="member-supply-record-list-create",
    ),
    path(
        "members/<str:member_id>/profile/",
        MemberProfileRetrieveAPIView.as_view(),
        name="member-profile-retrieve",
    ),
    # =====================================================
    # Invoice
    # =====================================================
    path(
        "invoices/<str:pk>/",
        InvoiceRetrieveUpdateAPIView.as_view(),
        name="invoice-retrieve-update",
    ),
    # =====================================================
    # Lookups
    # =====================================================
    path("lookup/<str:flag>/", LookupListAPIView.as_view(), name="lookup-list"),
]
