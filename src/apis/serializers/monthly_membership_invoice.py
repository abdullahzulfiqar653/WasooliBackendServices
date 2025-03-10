from rest_framework import serializers


class MonthlyMembershipInvoiceSerializer(serializers.Serializer):
    # class Meta:
    #     fields = []

    def create(self, validated_data):
        request = self.context.get("request")
        merchant = request.merchant
        members = merchant.members.all().prefetch_related()

        return super().create(validated_data)
