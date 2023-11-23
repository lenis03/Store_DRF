from django.urls import path, include
from rest_framework_nested import routers

from store import views

app_name = 'store'

router = routers.DefaultRouter()

router.register('products', views.ProductViewSet, basename='product')
router.register('categories', views.CategoryViewSet, basename='category')
router.register('carts', views.CartViewSet, basename='cart')

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

# urlpatterns = router.urls + products_router.urls

urlpatterns = [
    path('', include(router.urls + products_router.urls + carts_router.urls)),
]
