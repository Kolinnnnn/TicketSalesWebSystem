from django.contrib import admin
from .models import Event

class EventAdmin(admin.ModelAdmin):
    list_display = ('title','place')

    list_filter = ('place',)

admin.site.register(Event,EventAdmin)
