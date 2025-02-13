from django.http import JsonResponse
from django.utils import timezone
from .models import Seat
from events.models import Event
import re

def get_seats(request):
    row_id = request.GET.get('row_id')
    seats = Seat.objects.filter(row_id=row_id, is_available=True)

    seats_sorted = sorted(
            seats, 
            key=lambda seat: int(re.search(r'\d+', seat.name).group()) if re.search(r'\d+', seat.name) else float('inf')
        )

    seats_data = [{'id': seat.id, 'name': seat.name} for seat in seats_sorted]
    return JsonResponse({'seats': seats_data})

def reset_seats_for_past_events():
    past_events = Event.objects.filter(start__lt=timezone.now())
    for event in past_events:
        Seat.objects.filter(row__sector__place=event.place).update(is_available=True)