from decimal import Decimal
from rest_framework import serializers

from store.models import Product


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    unit_price_after_tax = serializers.SerializerMethodField()
    inventory = serializers.IntegerField()

    def get_unit_price_after_tax(self, product: Product):
        return round(product.unit_price * Decimal(1.09), 2)
