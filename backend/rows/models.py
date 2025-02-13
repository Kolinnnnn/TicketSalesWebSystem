from django.db import models
from sectors.models import Sector
from place.models import Place

class Row(models.Model):
    id = models.AutoField(primary_key=True)
    place = models.ForeignKey(Place,on_delete=models.CASCADE)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    row_number = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.name and 'Rząd' in self.name:
            try:
                self.row_number = int(''.join(filter(str.isdigit, self.name)))
            except ValueError:
                self.row_number = None
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        unique_together = ('sector', 'name')

    def __str__(self):
        if self.name.startswith("Rząd"):
            return self.name
        return f"Rząd {self.name}"