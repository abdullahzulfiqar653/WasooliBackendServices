from rest_framework import serializers
from apis.models.member_role import MemberRole, RoleChoices


class MemberRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberRole
        fields = ["id", "role"]

    def validate_role(self, value):
        if value not in [RoleChoices.CUSTOMER, RoleChoices.STAFF]:
            raise serializers.ValidationError(
                "Only 'Customer' or 'Staff' can be created."
            )
        return value
