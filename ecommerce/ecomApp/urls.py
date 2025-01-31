from django.urls import path 
from ecomApp import views
urlpatterns = [
    path('products',views.getProducts,name='getProducts'),
    path('categories',views.getCategories,name='getCategories'),
    path('categories/<str:category_name>/products/',views.getProductsByCategory, name='getProductsByCategory'),
    path('product/<int:product_id>/', views.get_product_detail, name='get_product_detail'),
    path('highest-rated-products/', views.get_most_popular_products, name='get_most_popular_products'),
    path('recommend-products/', views.recommend_products, name='recommend-products'),
    path('import-data/', views.import_data, name='import_data')
]