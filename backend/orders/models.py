from django.db import models
from events.models import Event
from seats.models import Seat
from tickets.models import TicketCategory
from login.models import User
from django.utils import timezone
from datetime import timedelta

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    ticket_type = models.ForeignKey(TicketCategory, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['id']

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    ticket_category = models.CharField(max_length=50, choices=TicketCategory.TICKET_CATEGORIES)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    expiration_time = models.DateTimeField(default=timezone.now() + timedelta(minutes=15))

    def is_expired(self):
        return timezone.now() > self.expiration_time