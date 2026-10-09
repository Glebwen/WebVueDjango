from django.contrib import admin

from bearings.models import Bearing
from bearings.models import Client
from bearings.models import Order
from bearings.models import Feedback
from bearings.models import OrderComposition

@admin.register(Bearing)
class BearingAdmin(admin.ModelAdmin):
    list_display = ['name', 'inner_d', 'outer_d', 'height', 'price', 'ammount']
    pass

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['number', 'client']
    pass

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['review', 'client']
    pass

@admin.register(OrderComposition)
class OrderCompAdmin(admin.ModelAdmin):
    list_display = ['order', 'bearing', "ammount"]
    pass

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone']
    pass