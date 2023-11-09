from django.urls import path

from store import views

app_name = 'store'

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
]
