from django.db.models import Q
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

from apis.models.member_role import RoleChoices
from apis.models.merchant_member import MerchantMember


class IsMerchantOrStaff(BasePermission):
    """
    Custom permission class to check if the user is a Merchant or Staff based on the username in the request data.
    """

    def has_permission(self, request, view):
        username = request.data.get("username")

        if not username:
            raise PermissionDenied("Username is required in the request data.")
        member = MerchantMember.objects.filter(
            Q(user__username=username)
            | Q(user__email=username)
            | Q(primary_phone=username)
        )
        if not member.exists():
            raise PermissionDenied("No user found with the provided username.")

        member = member.first()
        if not member.roles.filter(
            role__in=[RoleChoices.MERCHANT, RoleChoices.STAFF]
        ).exists():
            raise PermissionDenied("You are not allowed to login.")

        request.user = member.user
        return True
