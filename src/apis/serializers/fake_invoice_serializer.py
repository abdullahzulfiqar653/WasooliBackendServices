from rest_framework import serializers
from apis.models import Invoice


class FakeInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ["total_amount", "metadata"]
