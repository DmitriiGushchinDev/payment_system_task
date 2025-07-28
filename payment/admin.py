from django.contrib import admin
from .models import Item, Order, OrderItem, Discount, Tax

# Register your models here.

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price','description')
    list_filter = ('name',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('total_price', 'discount', 'tax',)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity')

class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'percentage')

class TaxAdmin(admin.ModelAdmin):
    list_display = ('type', 'percentage')

admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(Tax, TaxAdmin)
