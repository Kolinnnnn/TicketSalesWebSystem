from django.contrib import admin
from .models import Place

class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Place,PlaceAdmin)

