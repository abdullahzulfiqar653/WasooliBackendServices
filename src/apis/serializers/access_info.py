from rest_framework import serializers


class AccessInfoSerializer(serializers.Serializer):
    permissions = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField())
    )
    merchant_id = serializers.IntegerField()
    member_id = serializers.IntegerField()
