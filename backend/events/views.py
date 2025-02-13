from django.shortcuts import render
from .models import Event
from seats.models import Seat
from orders.models import Order
from django.utils import timezone
from sectors.models import Sector
from rows.models import Row
from django.db.models import Sum

def home(request):
    events = Event.objects.all()
    return render(request, 'home.html', {'events': events, 'username': request.user.email})

def event_detail(request, event_id):
    event = Event.objects.get(id=event_id)
    return render(request, 'event_detail.html', {'event': event})

def statistics(request):
    current_time = timezone.now()

    upcoming_events_data = []
    past_events_data = []

    events = Event.objects.all()
    for event in events:
        total_seats = Seat.objects.filter(row__sector__place=event.place).count()
        sold_seats = Order.objects.filter(event=event)
        sold_seats_count = sold_seats.count()
        total_revenue = sold_seats.aggregate(total=Sum('price'))['total'] or 0
        available_seats_count = total_seats - sold_seats_count

        normal_tickets_count = Order.objects.filter(event=event, ticket_type__category='normal').count()
        discount_tickets_count = Order.objects.filter(event=event, ticket_type__category='discount').count()

        sectors_data = []
        sectors = Sector.objects.filter(place=event.place)
        for sector in sectors:
            rows_data = []
            rows = Row.objects.filter(sector=sector)
            for row in rows:
                seats = Seat.objects.filter(row=row)
                available_seats = seats.filter(is_available=True).count()
                sold_seats = seats.filter(is_available=False).count()
                rows_data.append({
                    'row_name': row.name,
                    'available_seats': available_seats,
                    'sold_seats': sold_seats,
                })
            sectors_data.append({
                'sector_name': sector.name,
                'rows': rows_data,
            })

        event_data = {
            'title': event.title,
            'start': event.start,
            'total_seats': total_seats,
            'sold_seats': sold_seats_count,
            'available_seats': available_seats_count,
            'normal_tickets_sold': normal_tickets_count,
            'discount_tickets_sold': discount_tickets_count,
            'total_revenue': total_revenue,
            'sectors': sectors_data,
        }

        if event.start >= current_time:
            upcoming_events_data.append(event_data)
        else:
            past_events_data.append(event_data)

    context = {
        'upcoming_events': upcoming_events_data,
        'past_events': past_events_data,
    }
    return render(request, 'statistics.html', context)