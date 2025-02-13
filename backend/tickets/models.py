from django.db import models

class TicketCategory(models.Model):
    TICKET_CATEGORIES = [
        ('normal', 'Normalny'),
        ('discount', 'Ulgowy'),
    ]

    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=50, choices=TICKET_CATEGORIES, default='normal')

    class Meta:
        ordering = ['category']

    def __str__(self):
        return self.get_category_display()
