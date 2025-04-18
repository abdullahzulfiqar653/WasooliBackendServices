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
    MembershipStatusUpdateApiView,
    PublicMemberInvoiceListAPIView,
    MemberInvoiceListCreateAPIView,
    TransactionHistoryUpdateAPIView,
    MerchantMemberListCreateAPIView,
    MerchantDashboardRetrieveAPIView,
    MemberRetrieveUpdateDestroyAPIView,
    MemberSupplyRecordListCreateAPIView,
    MerchantFooterRetrieveUpdateAPIView,
    PublicMemberSupplyRecordListAPIView,
    PublicMembershipMerchantsListAPIView,
    PublicCustomerProfileRetrieveAPIView,
    MemberTransactionHistoryListCreateAPIView,
    MerchantMonthlyMembershipInvoiceCreateAPIView,
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
        "merchants/<str:merchant_id>/monthly-invoices/",
        MerchantMonthlyMembershipInvoiceCreateAPIView.as_view(),
        name="merchant-monthly-invoices",
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
    path(
        "merchants/<str:pk>/footer/",
        MerchantFooterRetrieveUpdateAPIView.as_view(),
        name="merchant-footer-update",
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
        "members/<str:member_id>/transaction-history/",
        MemberTransactionHistoryListCreateAPIView.as_view(),
        name="member-transaction-history-list-create",
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
    path(
        "members/<str:member_id>/status/",
        MembershipStatusUpdateApiView.as_view(),
        name="membership-status-update",
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
    # Transaction-History
    # =====================================================
    path(
        "transaction-history/<str:pk>/",
        TransactionHistoryUpdateAPIView.as_view(),
        name="transaction-history-update",
    ),
    # =====================================================
    # Public 
    # =====================================================
    path(
        "public/customer/<str:customer_code>/profile/<str:merchant_id>/",
        PublicCustomerProfileRetrieveAPIView.as_view(),
        name="public-customer-profile-retrieve",
    ),
    path(
        "public/customer/<str:customer_code>/merchants/",
        PublicMembershipMerchantsListAPIView.as_view(),
        name="public-membership-merchants-list",
    ),
    path(
        "public/customer/<str:customer_code>/invoices/<str:merchant_id>/",
        PublicMemberInvoiceListAPIView.as_view(),
        name="public-customer-invoice-list",
    ),
    path(
        "public/customer/<str:customer_code>/supply_record/<str:merchant_id>/",
        PublicMemberSupplyRecordListAPIView.as_view(),
        name="public-customer-supply-record-list",
    ),
    # =====================================================
    # Lookups
    # =====================================================
    path("lookup/<str:flag>/", LookupListAPIView.as_view(), name="lookup-list"),
]
