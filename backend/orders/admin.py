from django.contrib import admin
from .models import Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'event', 'sector', 'row', 'seat')

    def user_email(self, obj):
        return obj.user.email
    
    def event(self, obj):
        return obj.event.title

    def sector(self, obj):
        return obj.seat.row.sector.name

    def row(self, obj):
        return obj.seat.row.name

    def seat(self, obj):
        return obj.seat.name

admin.site.register(Order, OrderAdmin)
