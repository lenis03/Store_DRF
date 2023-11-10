from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . serializer import CategorySerializer, ProductSerializer
from .models import Category, Product


@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        products_queryset = Product.objects.select_related('category').all()
        serializer = ProductSerializer(
            products_queryset,
            many=True,
            context={'request': request}
            )
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('Everything Ok')


@api_view(['GET', 'PUT'])
def product_detail(request, pk):
    product = get_object_or_404(
        Product
        .objects
        .select_related('category'),
        pk=pk)

    if request.method == 'GET':
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view()
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serializer = CategorySerializer(category)

    return Response(serializer.data)
