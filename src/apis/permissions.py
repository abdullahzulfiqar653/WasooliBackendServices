from django.db.models import Q
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

from apis.models.merchant_member import MerchantMember, RoleChoices


class IsMerchantOrStaff(BasePermission):
    """
    Custom permission class to check if the user is a Merchant or Staff based on the username in the request data.
    """

    def has_permission(self, request, view):
        username = request.data.get("username")

        if not username:
            raise PermissionDenied("Username is required in the request data.")
        merchant_member = MerchantMember.objects.filter(
            Q(user__username=username)
            | Q(user__email=username)
            | Q(primary_phone=username)
        )
        if not merchant_member.exists():
            raise PermissionDenied("No user found with the provided username.")

        merchant_member = merchant_member.first()
        if merchant_member.role not in [RoleChoices.MERCHANT, RoleChoices.STAFF]:
            raise PermissionDenied("You are not allowed to login.")

        request.user = merchant_member.user
        return True
