from django.urls import path

from store import views

app_name = 'store'

urlpatterns = [
    path('products/', views.product_list),
    path('product/<int:id>/', views.product_detail),
]
