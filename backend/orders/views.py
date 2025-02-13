from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from events.models import Event
from tickets.models import TicketCategory
from .models import Order, Cart, CartItem
from seats.models import Seat
from sectors.models import Sector
from rows.models import Row
from login.models import User
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import io
import os
import base64
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import qrcode
import stripe
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from decimal import Decimal
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.http import JsonResponse
import logging
from login.utils import jwt_required
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)

@jwt_required
def buy_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)    
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'User is not logged in.')
        return redirect('login')

    user = get_object_or_404(User, id=user_id)
    clear_expired_cart_items(user)
    cart, created = Cart.objects.get_or_create(user=user)
    
    sectors_with_available_seats = []
    
    sectors = Sector.objects.filter(place=event.place)
    
    cart_item_seat_ids = cart.items.values_list('seat_id', flat=True)

    for sector in sectors:
        available_seats = Seat.objects.filter(row__sector=sector, is_available=True).exclude(id__in=cart_item_seat_ids)
        if available_seats.exists():
            sectors_with_available_seats.append(sector)

    available_seats = Seat.objects.filter(row__sector__place=event.place, is_available=True).exclude(id__in=cart_item_seat_ids)

    ticket_price = None

    if request.method == 'POST' and 'add_to_cart' in request.POST:
        category = request.POST.get('ticket_category')
        sector_id = request.POST.get('sector')
        row_id = request.POST.get('row')
        seat_id = request.POST.get('seat')

        sector = get_object_or_404(Sector, id=sector_id)
        row = get_object_or_404(Row, id=row_id)
        seat = get_object_or_404(Seat, id=seat_id, row_id=row_id, row__sector_id=sector_id)

        base_price = sector.price
        ticket_price = base_price if category == 'normal' else base_price * Decimal('0.5')

        return redirect('add_to_cart', event_id=event_id, seat_id=seat_id, ticket_category=category, ticket_price=str(ticket_price))

    return render(request, 'buy_ticket.html', {
        'event': event,
        'ticket_categories': TicketCategory.TICKET_CATEGORIES,
        'sectors': sectors_with_available_seats,
        'available_seats': available_seats,
        'ticket_price': ticket_price,
        'cart': cart.items.all()
    })

@jwt_required
def download_ticket(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return HttpResponse("Order not found.", status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{order.id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)

    pdfmetrics.registerFont(TTFont('DejaVuSans', 'static/fonts/DejaVuSans.ttf'))
    p.setFont("DejaVuSans", 22)
    
    x_margin = 100
    y_margin = 750

    p.setFillColor(colors.darkblue)
    p.drawString(x_margin, y_margin, f"Ticket for: {order.event.title}")

    p.setFont("DejaVuSans", 14)
    p.setFillColor(colors.black)
    p.drawString(x_margin, y_margin - 50, f"Date: {order.event.start.strftime('%d-%m-%Y %H:%M')}")
    p.drawString(x_margin, y_margin - 70, f"Place: {order.event.place.name}")

    p.setFont("DejaVuSans", 16)
    p.setFillColor(colors.red)
    p.drawString(x_margin, y_margin - 110, f"Row: {order.seat.row.name}, Sector: {order.seat.row.sector.name}")

    p.setFillColor(colors.black)
    p.setFont("DejaVuSans", 16)
    p.drawString(x_margin, y_margin - 140, f"Seat: {order.seat.name}")

    p.setFillColor(colors.green)
    p.drawString(x_margin, y_margin - 170, f"Price: {order.price} PLN")

    username = order.user.email.split('@')[0]

    p.setFont("DejaVuSans", 12)
    p.setFillColor(colors.black)
    p.drawString(x_margin, y_margin - 200, f"User: {username}")
    p.drawString(x_margin, y_margin - 220, f"Purchase Date: {(order.purchase_date + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")}")

    qr_data = (
        f"Order ID: {order.id}, "
        f"Event: {order.event.title}, "
        f"Sector: {order.seat.row.sector.name}, "
        f"Row: {order.seat.row.name}, "
        f"Seat: {order.seat.name}, "
        f"User: {username}"
    )
    qr_code = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr_code.add_data(qr_data)
    qr_code.make(fit=True)
    img = qr_code.make_image(fill='black', back_color='white')

    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    qr_image = ImageReader(img_buffer)
    p.drawImage(qr_image, 400, y_margin - 200, 2 * inch, 2 * inch)

    if order.event.place.stadiumPhoto:
        map_file_path = os.path.join(settings.MEDIA_ROOT, str(order.event.place.stadiumPhoto))
        try:
            map_image = ImageReader(map_file_path)
            p.drawImage(map_image, x_margin, y_margin - 450, width=300, height=200)
        except OSError:
            p.drawString(x_margin, y_margin - 450, "Map not available.")

    p.setStrokeColor(colors.gray)
    p.setLineWidth(1)
    p.line(x_margin, y_margin - 230, x_margin + 400, y_margin - 230)

    p.showPage()
    p.save()

    return response

def generate_ticket_pdf(order):
    """Generuje plik PDF na podstawie zamówienia."""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    pdfmetrics.registerFont(TTFont('DejaVuSans', 'static/fonts/DejaVuSans.ttf'))

    p.setFont("DejaVuSans", 22)
    p.setFillColor(colors.darkblue)

    y_margin = 750
    p.drawCentredString(300, y_margin, f"Bilet na: {order.event.title}")

    p.setFont("DejaVuSans", 14)
    p.setFillColor(colors.black)

    y_margin -= 50
    p.drawString(100, y_margin, f"Data wydarzenia: {order.event.start.strftime('%Y-%m-%d %H:%M')}")
    y_margin -= 20
    p.drawString(100, y_margin, f"Sektor: {order.seat.row.sector.name}")
    y_margin -= 20
    p.drawString(100, y_margin, f"Rząd: {order.seat.row.name}")
    y_margin -= 20
    p.drawString(100, y_margin, f"Miejsce: {order.seat.name}")
    y_margin -= 20
    p.drawString(100, y_margin, f"Kategoria: {order.ticket_type.category}")
    y_margin -= 20
    p.drawString(100, y_margin, f"Cena: {order.price} PLN")
    y_margin -= 20
    p.drawString(100, y_margin, f"Data zakupu: {(order.purchase_date + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")}")

    qr_data = (
        f"Order ID: {order.id}, "
        f"Event: {order.event.title}, "
        f"Sector: {order.seat.row.sector.name}, "
        f"Row: {order.seat.row.name}, "
        f"Seat: {order.seat.name}, "
        f"User: {order.user.email}"
    )
    qr_code = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr_code.add_data(qr_data)
    qr_code.make(fit=True)
    img = qr_code.make_image(fill='black', back_color='white')

    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    qr_image = ImageReader(img_buffer)
    p.drawImage(qr_image, 400, y_margin - 40, 2 * inch, 2 * inch)

    y_margin -= 120
    if order.event.place.stadiumPhoto:
        map_file_path = os.path.join(settings.MEDIA_ROOT, str(order.event.place.stadiumPhoto))
        try:
            map_image = ImageReader(map_file_path)
            p.drawImage(map_image, 100, y_margin - 200, width=300, height=200)
        except OSError:
            p.setFillColor(colors.red)
            p.drawString(100, y_margin - 200, "Brak dostępnej mapy stadionu.")

    p.showPage()
    p.save()
    buffer.seek(0)

    return ContentFile(buffer.read(), name=f"ticket_{order.id}.pdf")

@jwt_required
def show_ticket(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return HttpResponse("Order not found.", status=404)

    username = order.user.email.split('@')[0]

    qr_data = (
        f"Order ID: {order.id}, "
        f"Event: {order.event.title}, "
        f"Sector: {order.seat.row.sector.name}, "
        f"Row: {order.seat.row.name}, "
        f"Seat: {order.seat.name}, "
        f"User: {username}"
    )

    qr_code = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr_code.add_data(qr_data)
    qr_code.make(fit=True)

    img = qr_code.make_image(fill='black', back_color='white')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    qr_code_url = 'data:image/png;base64,' + base64.b64encode(img_buffer.getvalue()).decode('utf-8')

    purchase_date = (order.purchase_date + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    event_date = order.event.start.strftime("%Y-%m-%d %H:%M")

    return render(request, 'ticket_template.html', {
        'order': order,
        'user': username, 
        'qr_code_url': qr_code_url,
        'purchase_date': purchase_date,
        'event_date': event_date,
    })

stripe.api_key = settings.STRIPE_SECRET_KEY

@jwt_required
def create_checkout_session(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "User is not logged in.")
        return redirect('login')

    user = get_object_or_404(User, id=user_id)
    cart = Cart.objects.filter(user=user).first()

    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('dashboard')

    line_items = []
    metadata_cart_summary = []

    for item in cart.items.all():
        line_items.append({
            'price_data': {
                'currency': 'pln',
                'product_data': {
                    'name': f"Ticket for {item.event.title}",
                },
                'unit_amount': int(item.ticket_price * 100),
            },
            'quantity': 1,
        })

        metadata_cart_summary.append(f"{item.event.title} - Seat {item.seat.name}")

    metadata_summary = ', '.join(metadata_cart_summary)[:500]

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri(reverse('checkout-success')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('checkout-cancel')),
        client_reference_id=str(user.id),
        metadata={
            'cart_summary': metadata_summary,
            'user_id': str(user.id),
            'timestamp': timezone.now().isoformat(),
        }
    )

    return redirect(session.url, code=303)

@jwt_required
def checkout_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.error(request, "No session ID provided.")
        return redirect('dashboard')

    session = stripe.checkout.Session.retrieve(session_id)

    user_id = session.client_reference_id
    user = get_object_or_404(User, id=user_id)
    cart = Cart.objects.filter(user=user).first()

    if cart:
        with transaction.atomic():
            tickets = []
            for item in cart.items.all():
                ticket_category = TicketCategory.objects.get(category=item.ticket_category)
                
                order = Order.objects.create(
                    user=user,
                    event=item.event,
                    seat=item.seat,
                    ticket_type=ticket_category,
                    price=item.ticket_price,
                    is_paid=True
                )
                tickets.append(order)

                item.seat.is_available = False
                item.seat.save()

            cart.items.all().delete() 

            send_ticket_email(user, tickets)

    messages.success(request, "Your tickets have been successfully purchased.")
    return redirect('dashboard')

@jwt_required
def checkout_cancel(request):
    messages.error(request, "Your payment was canceled.")
    return redirect('dashboard')

@jwt_required
def cart(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'User is not logged in.')
        return redirect('login')
    
    user = get_object_or_404(User, id=user_id)
    clear_expired_cart_items(user)
    cart = Cart.objects.filter(user=user).first()
    cart_items = []
    total_price = 0

    if cart:
        cart_items = cart.items.all()
        total_price = sum(item.ticket_price for item in cart_items)

        cart_items_data = [
            {
                "id": item.id,
                "event_title": item.event.title,
                "seat_info": f"{item.seat.name}, {item.seat.row.name}, {item.seat.row.sector.name}",
                "ticket_category": item.ticket_category,
                "ticket_price": float(item.ticket_price),
                "expiration_time": item.expiration_time.isoformat()
            }
            for item in cart_items
        ]
    else:
        cart_items_data = []

    context = {
        "cart_items": cart_items,
        "cart_items_data": json.dumps(cart_items_data, cls=DjangoJSONEncoder),
        "total_price": total_price,
    }

    return render(request, 'cart.html', context)

@jwt_required
def clear_cart(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    cart = Cart.objects.filter(user_id=user_id).first()
    
    if cart:
        for item in cart.items.all():
            seat = item.seat
            seat.is_available = True
            seat.save()
        
        cart.items.all().delete()
        messages.success(request, "Cart has been cleared.")
    else:
        messages.info(request, "Your cart is already empty.")

    return redirect('cart')

@jwt_required
def add_to_cart(request, event_id, seat_id, ticket_category, ticket_price):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'User is not logged in.')
        return redirect('login')

    user = get_object_or_404(User, id=user_id)
    event = get_object_or_404(Event, id=event_id)
    seat = get_object_or_404(Seat, id=seat_id)
    ticket_price = Decimal(ticket_price)

    cart, created = Cart.objects.get_or_create(user=user)

    if cart.items.count() >= 5:
        messages.error(request, "You already have 5 tickets in your cart.")
        return redirect('buy_ticket', event_id=event_id)

    new_expiration_time = timezone.now() + timedelta(minutes=15)

    existing_item = CartItem.objects.filter(cart=cart, event=event, seat=seat).first()
    if existing_item:
        logger.info(f"Deleting expired item: ID {existing_item.id}, Expiration Time: {existing_item.expiration_time}")
        existing_item.delete()

    new_item = CartItem.objects.create(
        cart=cart,
        event=event,
        seat=seat,
        ticket_category=ticket_category,
        ticket_price=ticket_price,
        expiration_time=new_expiration_time
    )
    seat.is_available = False
    seat.save()

    logger.info(f"Added new item to cart: ID {new_item.id}, Expiration Time: {new_expiration_time}")

    messages.success(request, "Ticket added to cart.")
    return redirect('buy_ticket', event_id=event_id)

@jwt_required
def remove_from_cart(request, item_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "User is not logged in.")
        return redirect('login')

    user = get_object_or_404(User, id=user_id)
    
    cart = Cart.objects.filter(user=user).first()

    if cart:
        cart_item = cart.items.filter(id=item_id).first()
        if cart_item:
            cart_item.seat.is_available = True
            cart_item.seat.save()
            
            cart_item.delete()
            messages.success(request, "Ticket has been removed from your cart.")
        else:
            messages.error(request, "This ticket is not in your cart.")
    else:
        messages.error(request, "You do not have a cart.")

    return redirect('cart')

def clear_expired_cart_items(user):
    """Funkcja usuwająca wygasłe bilety z koszyka użytkownika."""
    cart = Cart.objects.filter(user=user).first()
    if cart:
        expired_items = cart.items.filter(expiration_time__lt=timezone.now())
        for item in expired_items:
            item.seat.is_available = True
            item.seat.save()
        expired_items.delete()

@csrf_exempt
def clear_expired_items(request):
    """Widok wywoływany przez AJAX do usunięcia wygasłych biletów globalnie."""
    try:
        clear_expired_cart_items_for_all_users()
        return JsonResponse({'status': 'expired items cleared'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def clear_expired_cart_items_for_all_users():
    """Usuwa wygasłe bilety z koszyków wszystkich użytkowników."""
    expired_items = CartItem.objects.filter(expiration_time__lt=timezone.now())
    for item in expired_items:
        item.seat.is_available = True
        item.seat.save()
    expired_items.delete()

def send_ticket_email(user, tickets):
    subject = "Your Tickets"
    from_email = settings.EMAIL_HOST_USER
    to_email = [user.email]

    text_content = "Thank you for your purchase. Attached are your tickets."
    html_content = render_to_string('ticket_email.html', {
        'user': user,
        'tickets': tickets
    })

    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")

    for ticket in tickets:
        pdf = generate_ticket_pdf(ticket)
        email.attach(pdf.name, pdf.read(), 'application/pdf')

    email.send()