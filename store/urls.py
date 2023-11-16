from django.urls import path, include
from rest_framework.routers import DefaultRouter

from store import views

app_name = 'store'

router = DefaultRouter()

router.register('products', views.ProductViewSet)
router.register('categories', views.CategoryViewSet)

# urlpatterns = router.urls

urlpatterns = [
    path('', include(router.urls)),
]
