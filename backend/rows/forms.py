from django import forms
from .models import Row
from sectors.models import Sector
from django.urls import reverse

class RowAdminForm(forms.ModelForm):
    row_count = forms.IntegerField(
        required=False, 
        label="Liczba rzędów do dodania", 
        help_text="Jeśli wypełnisz, doda tyle nowych rzędów z nazwami Rząd 1, Rząd 2 itd."
    )

    class Meta:
        model = Row
        fields = ['place', 'sector', 'row_count']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        data_url = reverse('get_sectors_admin')
        self.fields['place'].widget.attrs.update({
            'data-url': data_url
        })

        self.fields['sector'].queryset = Sector.objects.none()

        if 'place' in self.data:
            try:
                place_id = int(self.data.get('place'))
                self.fields['sector'].queryset = Sector.objects.filter(place_id=place_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['sector'].queryset = self.instance.sector.place.sector_set.all()