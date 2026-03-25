from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('product', views.product, name='product'),
    path('product/<int:id>', views.product_details, name='product_details'),
    path('signin', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('logout', views.user_logout, name='logout'),
    
    # Cart URLs
    path('cart', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:product_id>', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:cart_id>', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout URLs
    path('checkout', views.checkout, name='checkout'),
    path('place-order', views.place_order, name='place_order'),
    
    # Order Status
    path('my-orders', views.my_orders, name='my_orders'),
    
    # User Profile
    path('my-profile', views.my_profile, name='my_profile'),
    
    # Admin Dashboard
    path('admin-dashboard', views.admin_dashboard, name='admin_dashboard'),
    
    # Support URLs
    path('contact_us', views.contact_us, name='contact_us'),
    path('faq', views.faq, name='faq'),
    
    # Chatbot
    # Admin Product Management
    path('manage-product/add', views.admin_add_product, name='admin_add_product'),
    path('manage-product/update/<int:id>', views.admin_update_product, name='admin_update_product'),
    path('manage-product/delete/<int:id>', views.admin_delete_product, name='admin_delete_product'),
    
    # Eco Features
    path('carbon-calculator', views.carbon_calculator, name='carbon_calculator'),
    
    # Waste Pickup Features
    path('request-pickup/', views.request_pickup, name='request_pickup'),
    path('my-pickups/', views.my_pickups, name='my_pickups'),
    path('manage-pickups/', views.admin_manage_pickups, name='admin_manage_pickups'),


]


