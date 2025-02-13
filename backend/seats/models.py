from django.db import models
from rows.models import Row
from place.models import Place
from sectors.models import Sector
from django.core.exceptions import ValidationError

class Seat(models.Model):
    id = models.AutoField(primary_key=True)
    place = models.ForeignKey(Place,on_delete=models.CASCADE)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    row = models.ForeignKey(Row,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)
    seat_number = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['row', 'seat_number']
        unique_together = ('row', 'seat_number')

    def __str__(self):
        return self.name
    
    def clean(self):
        if self.name.startswith("Miejsce"):
            try:
                self.seat_number = int(self.name.split(" ")[1])
            except (IndexError, ValueError):
                raise ValidationError("Invalid seat name format; expected 'Miejsce <number>'.")