from django.contrib import admin
from .models import TicketCategory

class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ('category',)
    search_fields = ('category',)
    list_filter = ('category',)
    
admin.site.register(TicketCategory,TicketCategoryAdmin)