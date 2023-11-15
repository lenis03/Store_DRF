from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from . serializer import CategorySerializer, ProductSerializer
from .models import Category, Product


class ProductList(APIView):
    def get(self, request):
        products_queryset = Product.objects.select_related('category').all()
        serializer = ProductSerializer(
            products_queryset,
            many=True,
            context={'request': request}
            )
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetail(APIView):
    def setup(self, request, *args, **kwargs):
        self.product = get_object_or_404(
            Product
            .objects
            .select_related('category'),
            pk=kwargs['pk'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        serializer = ProductSerializer(self.product, context={'request': request})
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        serializer = ProductSerializer(self.product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        if self.product.order_items.count() > 0:
            return Response({
                'error':
                    'There is some order items including this product.'
                    'Please remove them first'},
                    status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryList(APIView):
    def get(self, request):
        categories_queryset = Category\
            .objects\
            .prefetch_related('products').all()
        serializer = CategorySerializer(categories_queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryDetail(APIView):
    def setup(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category.objects.prefetch_related('products'),
            pk=kwargs['pk'])

        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        serializer = CategorySerializer(self.category)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        serializer = CategorySerializer(instance=self.category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        if self.category.products.count() > 0:
            return Response({
                'error':
                'There are a number of products that subset this category,'
                'Please remove them first.'
                }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
