from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet

from .filters import ProductFilter
from .models import Cart, CartItem, Category, Comment, Customer, Order, OrderItem, Product
from .paginations import DefaultPagination
from .permissions import IsAdminOrCreateAndRetrieve, IsAdminOrReadOnly, SendPrivateEmailToCustomerPermission
from .serializer import AddCartItemSerializer, AdminOrderSerializer, CartItemSerializer, CartSerializer, CategorySerializer, ClientOrderSerializer, CustomerSerializer, ProductSerializer, CommentSerializer, UpdateCartItemSerializer


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related('category').all()
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    # filterset_fields = ['category_id', 'inventory']
    filterset_class = ProductFilter
    ordering_fields = ['name', 'unit_price', 'inventory']
    search_fields = ['name', 'category__title']
    pagination_class = DefaultPagination
    ordering = ['id']
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, pk):
        product = get_object_or_404(
            Product.objects.select_related('category'),
            pk=pk
            )
        if product.order_items.count() > 0:
            return Response({
                'error':
                    'There is some order items including this product.'
                    'Please remove them first'},
                    status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.prefetch_related('products').all()
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, pk):
        category = get_object_or_404(
            Category.objects.prefetch_related('products'),
            pk=pk
            )
        if category.products.count() > 0:
            return Response({
                'error':
                'There are a number of products that subset this category,'
                'Please remove them first.'
                }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrCreateAndRetrieve]

    def get_queryset(self):
        product_pk = self.kwargs['product_pk']
        return Comment.objects.filter(
            status=Comment.COMMENT_STATUS_APPROVED,
            product_id=product_pk).all()

    def get_serializer_context(self):
        return {'product_pk': self.kwargs['product_pk']}


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        cart_pk = self.kwargs['cart_pk']
        return CartItem.objects.select_related(
            'product'
            )\
            .filter(cart_id=cart_pk)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_pk': self.kwargs['cart_pk']}


class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.prefetch_related('items__product').all()
    lookup_value_regex = '[0-9a-fA-F]{8}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{12}'


class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user_id = request.user.id
        customer = Customer.objects.get(user_id=user_id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(instance=customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=True, permission_classes=[SendPrivateEmailToCustomerPermission])
    def send_private_email(self, request, pk):
        return Response(f'Sending private email to customer {pk=}')


class OrderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.select_related('customer__user')\
            .prefetch_related(
                Prefetch(
                    'items',
                    queryset=OrderItem.objects.select_related('product')
                )
            ).all()
        if user.is_staff:
            return queryset
        return queryset.filter(customer__user=user.id)

    def get_serializer_class(self):
        user = self.request.user
        if user.is_staff:
            return AdminOrderSerializer
        return ClientOrderSerializer
