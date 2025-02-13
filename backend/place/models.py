from django.db import models

class Place(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    stadiumPhoto = models.ImageField(upload_to='stadium_photos/', blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

