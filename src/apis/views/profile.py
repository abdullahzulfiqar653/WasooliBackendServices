from rest_framework import generics
from rest_framework.response import Response
from apis.permissions import IsMerchantOrStaff
from django.contrib.auth.models import Permission


class AccessInfoRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsMerchantOrStaff]
    serializer_class = None

    def retrieve(self, request, *args, **kwargs):
        direct_permissions = request.user.user_permissions.all()
        group_permissions = Permission.objects.filter(group__user=request.user)
        all_permissions = direct_permissions | group_permissions

        print(all_permissions)
        grouped_permissions = {}
        print(request.user)

        for perm in all_permissions.distinct():
            model_name = perm.content_type.model
            grouped_permissions.setdefault(model_name, []).append(perm.codename)

        for model, actions in grouped_permissions.items():
            grouped_permissions[model] = sorted(set(actions))

        return Response(
            {
                "permissions": grouped_permissions,
                "merchant_id": request.merchant.id,
                "member_id": request.user.profile.id,
            }
        )
