from django.db import models

class User(models.Model):
    id = models.AutoField(unique=True,primary_key=True)
    email = models.EmailField(max_length=100)
    passwordHash = models.CharField(max_length=100)

    class Meta:
        managed = True,
        db_table = 'user'
    