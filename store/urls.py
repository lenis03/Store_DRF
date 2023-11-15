from django.urls import path

from store import views

app_name = 'store'

urlpatterns = [
    path('products/', views.ProductList.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductDetail.as_view(), name='product_detail'),
    path('categories/', views.CategoryList.as_view(), name='category_list'),
    path('categories/<int:pk>/', views.CategoryDetail.as_view(), name='category_detail'),
]
