from django import forms
from django.urls import reverse
from .models import Seat
from rows.models import Row
from sectors.models import Sector

class SeatAdminForm(forms.ModelForm):
    seat_count = forms.IntegerField(
        required=False,
        label="Liczba miejsc do dodania",
        help_text="Jeśli wypełnisz, doda tyle nowych miejsc z nazwami Miejsce 1, Miejsce 2 itd."
    )

    class Meta:
        model = Seat
        fields = ['place', 'sector', 'row', 'seat_count']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['place'].widget.attrs.update({
            'data-url': reverse('get_sectors_admin')
        })
        self.fields['sector'].widget.attrs.update({
            'data-url': reverse('get_rows_admin')
        })
        
        self.fields['sector'].queryset = Sector.objects.none()
        self.fields['row'].queryset = Row.objects.none()

        if 'place' in self.data:
            try:
                place_id = int(self.data.get('place'))
                self.fields['sector'].queryset = Sector.objects.filter(place_id=place_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['sector'].queryset = Sector.objects.filter(place=self.instance.place)
        
        if 'sector' in self.data:
            try:
                sector_id = int(self.data.get('sector'))
                self.fields['row'].queryset = Row.objects.filter(sector_id=sector_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['row'].queryset = Row.objects.filter(sector=self.instance.sector)