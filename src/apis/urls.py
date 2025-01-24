from django.urls import path, include
from apis.views import (
    OTPView,
    LookupListAPIView,
    RefreshTokenAPIView,
    InvoiceMarkPaidAPIView,
    AccessInfoRetrieveAPIView,
    PreSignedUrlCreateAPIView,
    MemberRetrieveByPhoneAPIView,
    InvoiceRetrieveUpdateAPIView,
    MemberInvoiceListCreateAPIView,
    MerchantMemberListCreateAPIView,
    MemberRetrieveUpdateDestroyAPIView,
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
    # =====================================================
    # Invoice
    # =====================================================
    path(
        "invoices/<str:pk>/",
        InvoiceRetrieveUpdateAPIView.as_view(),
        name="invoice-retrieve-update",
    ),
    path(
        "invoices/<str:invoice_id>/mark-paid/",
        InvoiceMarkPaidAPIView.as_view(),
        name="invoice-mark-paid",
    ),
    # =====================================================
    # Lookups
    # =====================================================
    path("lookup/<str:flag>/", LookupListAPIView.as_view(), name="lookup-list"),
]
