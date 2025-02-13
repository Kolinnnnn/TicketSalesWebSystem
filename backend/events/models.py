from django.db import models
from place.models import Place

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    start = models.DateTimeField()

    class Meta:
        ordering = ['start']

    def __str__(self):
        return self.title

