from rest_framework import serializers

from store.models import Product

DOLLORS_TO_RIALS = 500000


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    inventory = serializers.IntegerField()
    price_rials = serializers.SerializerMethodField()

    def get_price_rials(self, product: Product):
        return int(product.unit_price * DOLLORS_TO_RIALS)
