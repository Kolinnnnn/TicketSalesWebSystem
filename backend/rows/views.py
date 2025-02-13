from django.http import JsonResponse
from .models import Row
from seats.models import Seat
from sectors.models import Sector
import json
import re

def get_rows(request):
    sector_id = request.GET.get('sector_id')
    rows_with_available_seats = []

    rows = Row.objects.filter(sector_id=sector_id)

    rows_sorted = sorted(
        rows,
        key=lambda row: int(re.search(r'\d+', row.name).group()) if re.search(r'\d+', row.name) else float('inf')
    )

    for row in rows_sorted :
        available_seats = Seat.objects.filter(row=row, is_available=True)
        rows_with_available_seats.append({
            'id': row.id,
            'name': row.name,
            'has_seats': available_seats.exists()
        })

    return JsonResponse({'rows': rows_with_available_seats})

def get_rows_admin(request):
    sector_id = request.GET.get('sector_id')
    if sector_id:
        rows = Row.objects.filter(sector_id=sector_id).values('id', 'name')
        return JsonResponse(list(rows), safe=False)
    return JsonResponse({'error': 'No sector_id provided'}, status=400)

def add_multiple_rows(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        place_id = data.get('place_id')
        sector_id = data.get('sector_id')
        row_count = data.get('row_count')

        try:
            sector = Sector.objects.get(id=sector_id, place_id=place_id)
            last_row_number = Row.objects.filter(sector=sector).count()

            for i in range(1, row_count + 1):
                Row.objects.create(
                    name=f"Rzad {last_row_number + i}",
                    place_id=place_id,
                    sector=sector
                )
            return JsonResponse({"success": True})

        except Sector.DoesNotExist:
            return JsonResponse({"success": False, "error": "Sector not found."})

    return JsonResponse({"success": False, "error": "Invalid request."})