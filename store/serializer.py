from decimal import Decimal
from django.utils.text import slugify
from rest_framework import serializers

from .models import Cart, Category, Comment, Product


class CategorySerializer(serializers.ModelSerializer):
    number_of_product = serializers.IntegerField(source='products.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'number_of_product']

    def validate(self, data):
        if len(data['title']) < 3:
            raise serializers.ValidationError(
                'Category title length should be at least 3.'
                )
        return data


class ProductSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255, source='name')
    price = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        source='unit_price'
        )
    unit_price_after_tax = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'price',
            'unit_price_after_tax',
            'category',
            'inventory',
            'description',
            ]

    def get_unit_price_after_tax(self, product: Product):
        return round(product.unit_price * Decimal(1.09), 2)

    def validate(self, data):
        if len(data['name']) < 6:
            raise serializers.ValidationError(
                'Product title length should be at least 6'
                )
        return data

    def create(self, validated_data):
        product = Product(**validated_data)
        product.slug = slugify(product.name)
        product.save()

        return product


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'name', 'body']

    def create(self, validated_data):
        product_pk = self.context['product_pk']
        return Comment.objects.create(
            product_id=product_pk,
            **validated_data
            )


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'created_at']
