from django.apps import apps
from django.db.models import Q
from rest_framework import exceptions
from rest_framework import permissions

from apis.models.member_role import RoleChoices
from apis.models.merchant_member import MerchantMember


class IsAllowedToLogin(permissions.BasePermission):
    """
    Custom permission class to check if the user is a Merchant or Staff based on the username in the request data.
    """

    def has_permission(self, request, view):
        username = request.data.get("username")

        if not username:
            raise exceptions.PermissionDenied(
                "Username is required in the request data."
            )
        member = MerchantMember.objects.filter(
            Q(user__username=username)
            | Q(user__email=username)
            | Q(primary_phone=username)
        )
        if not member.exists():
            raise exceptions.PermissionDenied(
                "No user found with the provided username."
            )

        member = member.first()
        if not member.roles.filter(
            role__in=[RoleChoices.MERCHANT, RoleChoices.STAFF]
        ).exists():
            raise exceptions.PermissionDenied("You are not allowed to login.")

        request.user = member.user
        return True


class IsMerchantOrStaff(permissions.BasePermission):
    def get_instance(self, queryset, instance_id):
        try:
            instance = queryset.get(id=instance_id)
        except queryset.model.DoesNotExist:
            raise exceptions.NotFound
        return instance

    def get_merchant(self, request, view):
        match request.path:
            case str(s) if s.startswith("/api/merchant/"):
                if not hasattr(request, "merchant"):
                    Merchant = apps.get_model("apis", "Merchant")
                    merchant_id = view.kwargs.get("pk") or view.kwargs.get(
                        "merchant_id"
                    )
                    queryset = Merchant.objects.all()
                    request.merchant = self.get_instance(queryset, merchant_id)
                merchant = request.merchant
            case _:
                merchant = None
        return merchant

    def is_authenticated(self, request):
        return bool(request.user and request.user.is_authenticated)

    def is_in_merchant(self, request, view):
        if not self.is_authenticated(request):
            return False

        merchant = self.get_merchant(request, view)
        if not merchant:
            return False

        # Check if the user is a merchant
        if merchant.owner == request.user:
            return merchant

        # Check if the user is a staff member for the merchant
        # Assuming `request.user.profile.roles` contains the user's roles,
        # and the role is of type 'Staff' and associated with the merchant
        if request.user.profile.roles.filter(
            role=RoleChoices.STAFF, member__merchant=merchant
        ).exists():
            return merchant

    def has_permission(self, request, view):
        merchant = self.is_in_merchant(request, view)
        if not merchant:
            return False
        return True
