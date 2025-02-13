from django import forms
from .models import TicketCategory 
from sectors.models import Sector
from rows.models import Row
from seats.models import Seat

class TicketPurchaseForm(forms.Form):
    ticket_category = forms.ModelChoiceField(queryset=TicketCategory.objects.all(), label="Ticket Category")
    sector = forms.ModelChoiceField(queryset=Sector.objects.all(), label="Sector")
    row = forms.ModelChoiceField(queryset=Row.objects.none(), label="Row")
    seat = forms.ModelChoiceField(queryset=Seat.objects.none(), label="Seat")

    def __init__(self, event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ticket_category'].queryset = TicketCategory.objects.filter(event=event)
        self.fields['sector'].queryset = Sector.objects.filter(place=event.place)

        if 'sector' in self.data:
            try:
                sector_id = int(self.data.get('sector'))
                self.fields['row'].queryset = Row.objects.filter(sector_id=sector_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['row'].queryset = Row.objects.none()

        if 'row' in self.data:
            try:
                row_id = int(self.data.get('row'))
                self.fields['seat'].queryset = Seat.objects.filter(row_id=row_id, is_available=True).order_by('name')
            except (ValueError, TypeError):
                self.fields['seat'].queryset = Seat.objects.none()
