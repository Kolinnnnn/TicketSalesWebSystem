from django.contrib import admin
from .models import Row
from .forms import RowAdminForm

class RowAdmin(admin.ModelAdmin):
    form = RowAdminForm
    list_display = ('display_name', 'sector', 'place_name')
    list_filter = ('sector__place',)
    ordering = ['row_number']

    class Media:
        js = ('/static/js/rows/row_admin.js',)

    def display_name(self, obj):
        return obj.name
    display_name.short_description = 'Name'
    display_name.admin_order_field = None

    def save_model(self, request, obj, form, change):
        row_count = form.cleaned_data.get('row_count')
        if row_count:
            sector = form.cleaned_data.get('sector')
            place = form.cleaned_data.get('place')
            last_row_number = Row.objects.filter(sector=sector).count()

            for i in range(1, row_count + 1):
                new_row = Row(
                    name=f"Rząd {last_row_number + i}",
                    place=place,
                    sector=sector
                )
                new_row.save()
        else:
            if not obj.name:
                last_row_number = Row.objects.filter(sector=obj.sector).count()
                obj.name = f"Rząd {last_row_number + 1}"
            super().save_model(request, obj, form, change)

    def event_name(self, obj):
        related_events = obj.sector.place.event_set.all()
        if related_events.exists():
            return ', '.join([event.title for event in related_events])
        return "No Event"
    
    event_name.short_description = 'Event'

    def place_name(self, obj):
        return obj.sector.place.name
    
    place_name.short_description = 'Place'
    
admin.site.register(Row, RowAdmin)

