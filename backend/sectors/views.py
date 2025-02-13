from django.http import JsonResponse
from .models import Sector
from seats.models import Seat

def get_sectors(request, event_id):
    sectors_with_available_seats = []

    sectors = Sector.objects.filter(place__event__id=event_id)

    for sector in sectors:
        available_seats = Seat.objects.filter(row__sector=sector, is_available=True)
        if available_seats.exists():
            sectors_with_available_seats.append({
                'id': sector.id,
                'name': sector.name,
            })

    return JsonResponse({'sectors': sectors_with_available_seats})

def get_sectors_admin(request):
    place_id = request.GET.get('place_id')
    print(f"Received place_id: {place_id}")
    sectors = Sector.objects.filter(place_id=place_id).values('id', 'name')
    return JsonResponse(list(sectors), safe=False)