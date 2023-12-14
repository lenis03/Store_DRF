from decimal import Decimal
from django.utils.text import slugify
from django.db import transaction
from rest_framework import serializers

from .models import Cart, CartItem, Category, Comment, Customer, Order, OrderItem, Product


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


class CartProductSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'unit_price']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

    def create(self, validated_data):
        cart_pk = self.context['cart_pk']
        product = validated_data.get('product')
        quantity = validated_data.get('quantity')

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_pk,
                product_id=product.id
                )
            cart_item.quantity += quantity
            cart_item.save()

        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                cart_id=cart_pk,
                **validated_data
                )

        self.instance = cart_item
        return cart_item


class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerialzer()
    item_total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'item_total_price']

    def get_item_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
        read_only_fields = ['id']

    def get_total_price(self, cart: Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user', 'phone_number', 'birth_date']
        read_only_fields = ['user']


class OrderCustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255, source='user.first_name')
    last_name = serializers.CharField(max_length=255, source='user.last_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Customer
        fields = ['id', 'user', 'first_name', 'last_name', 'email']


class OrderItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'unit_price']


class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderItemProductSerializer()
    item_total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'item_total_price']

    def get_item_total_price(self, order_item: OrderItem):
        return order_item.product.unit_price * order_item.quantity


class AdminOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = OrderCustomerSerializer()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'items', 'total_price', 'status', 'datetime_created']

    def get_total_price(self, order: Order):
        return sum([item.quantity * item.product.unit_price  for item in order.items.all()])


class ClientOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'items', 'total_price', 'status', 'datetime_created']

    def get_total_price(self, order: Order):
        return sum([item.product.unit_price * item.quantity for item in order.items.all()])


class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):

        if not Cart.objects.filter(id=cart_id).exists():
            raise serializers.ValidationError('There is no cart with this cart id!')

        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('Your cart is empty. Please add some product to it first!')

        return cart_id

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # The second method:
        # try:
        #     if Cart.objects.prefetch_related('items').get(id=cart_id).items.count() == 0:
        #         raise serializers.ValidationError('Your cart is empty. Please add some product to it first!')
        # except Cart.DoesNotExist:
        #     raise serializers.ValidationError('There is no cart with this cart id!')
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def save(self):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']
            customer = Customer.objects.get(user_id=user_id)
            
# ///////////////////////////////////////////////////////////////////////////
            # The second method:
            # cart_items = Cart.objects.prefetch_related('items').get(id=cart_id).items.all()
# /////////////////////////////////////////////////////////////////////////////

            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            order = Order()
            order.customer = customer
            order.save()

            order_items = [
                OrderItem(
                    order=order,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.unit_price
                ) for cart_item in cart_items
                ]

# /////////////////////////////////////////////////////
            # second method:
            # order_items = list()
            # for cart_item in cart_items:
            #     order_item = OrderItem()
            #     order_item.order = order
            #     order_item.product_id = cart_item.product_id
            #     order_item.quantity = cart_item.quantity
            #     order_item.unit_price = cart_item.product.unit_price
            #     order_items.append(order_item)
# ////////////////////////////////////////////////////////

            OrderItem.objects.bulk_create(order_items)

            Cart.objects.get(pk=cart_id).delete()

            return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
