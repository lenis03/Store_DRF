from django.urls import path, include
from rest_framework_nested import routers

from store import views

app_name = 'store'

router = routers.DefaultRouter()

router.register('products', views.ProductViewSet, basename='product')
router.register('categories', views.CategoryViewSet, basename='category')
router.register('carts', views.CartViewSet, basename='cart')
router.register('customers', views.CustomerViewSet, basename='customer')
router.register('orders', views.OrderViewSet, basename='order')

products_router = routers.NestedDefaultRouter(
    router,
    'products',
    lookup='product'
    )

products_router.register(
    'comments',
    views.CommentViewSet,
    basename='product-comments'
    )

carts_router = routers.NestedDefaultRouter(
    router,
    'carts',
    lookup='cart'
)

carts_router.register(
    'items',
    views.CartItemViewSet,
    basename='cart-items'
)

order_router = routers.NestedDefaultRouter(
    router,
    'orders',
    lookup='order'
)

order_router.register(
    'items',
    views.OrderItemViewSet,
    basename='order-items')

# urlpatterns = router.urls + products_router.urls

urlpatterns = [
    path('orders/return_to_cart/', views.OrderToCartView.as_view(), name='order_to_cart'),
    path('', include(
                router.urls
                +
                products_router.urls
                +
                carts_router.urls
                +
                order_router.urls)),
    path('orders/<int:order_id>/pay/', views.OrderPayView.as_view(), name='order-pay'),
    path('orders/verify', views.OrderVerifyView.as_view(), name='order_verify')
]
