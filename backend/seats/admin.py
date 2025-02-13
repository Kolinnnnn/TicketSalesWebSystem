from django.contrib import admin
from .models import Seat
from .forms import SeatAdminForm

class SeatAdmin(admin.ModelAdmin):
    form = SeatAdminForm
    list_display = ('display_name', 'row_name', 'sector_name', 'place_name')
    list_filter = ('row__sector__place',)

    class Media:
        js = ('/static/js/seats/seat_admin.js',)

    def display_name(self, obj):
        return obj.name
    display_name.short_description = 'Name'
    display_name.admin_order_field = None

    def save_model(self, request, obj, form, change):
        seat_count = form.cleaned_data.get('seat_count')
        if seat_count:
            row = form.cleaned_data.get('row')
            last_seat_number = Seat.objects.filter(row=row).count()

            for i in range(1, seat_count + 1):
                new_seat = Seat(
                    name=f"Miejsce {last_seat_number + i}",
                    place=form.cleaned_data.get('place'),
                    sector=form.cleaned_data.get('sector'),
                    row=row
                )
                new_seat.save()
        else:
            if not obj.name:
                last_seat_number = Seat.objects.filter(row=obj.row).count()
                obj.name = f"Miejsce {last_seat_number + 1}"
            super().save_model(request, obj, form, change)

    def row_name(self, obj):
        return obj.row.name
    row_name.short_description = 'Row'

    def sector_name(self, obj):
        return obj.row.sector.name if obj.row and obj.row.sector else "No Sector"
    sector_name.short_description = 'Sector'

    def place_name(self, obj):
        return obj.row.sector.place.name
    place_name.short_description = 'Place'

    def event_name(self, obj):
        related_events = obj.row.sector.place.event_set.all()
        if related_events.exists():
            return ', '.join([event.title for event in related_events])
        return "No Event"
    event_name.short_description = 'Event'

admin.site.register(Seat,SeatAdmin)
