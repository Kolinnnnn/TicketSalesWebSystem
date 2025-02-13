from django.db import models
from place.models import Place

class Sector(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['name']
        unique_together = ('place', 'name')

    def __str__(self):
        return self.name
