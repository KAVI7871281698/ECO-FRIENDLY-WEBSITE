from django.contrib import admin
from .models import Register, Category, product, Order, OrderItem, CarbonFootprint, PickupRequest

@admin.register(Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'city', 'role')
    list_editable = ('role',)
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'city')
    list_filter = ('role', 'city')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'get_category', 'product_price')
    list_filter = ('product_Categorie',)
    search_fields = ('product_name', 'product_des')

    def get_category(self, obj):
        return obj.product_Categorie.name if obj.product_Categorie else "No Category"
    get_category.short_description = 'Category'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'total_price', 'status', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'email', 'phone')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')

@admin.register(CarbonFootprint)
class CarbonFootprintAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_carbon', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__first_name')

@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'waste_type', 'pickup_date', 'status', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'waste_type', 'pickup_date', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'address')

