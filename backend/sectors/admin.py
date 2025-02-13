from django.contrib import admin
from .models import Sector

class SectorAdmin(admin.ModelAdmin):
    list_display = ('name','place_name')

    list_filter = ('place',)

    def event_name(self, obj):
        related_events = obj.place.event_set.all()
        if related_events.exists():
            return ', '.join([event.title for event in related_events])
        return "No Event"
    
    event_name.short_description = 'Event'

    def place_name(self, obj):
        return obj.place.name if obj.place else "No Place"
    
    place_name.short_description = 'Place'

admin.site.register(Sector, SectorAdmin)

