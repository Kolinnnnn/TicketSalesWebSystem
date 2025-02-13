from django.contrib import admin
from django.urls import path
from login import views as loginViews
from register import views as registerViews
from events import views as eventViews
from orders import views as orderViews
from seats import views as seatViews
from rows import views as rowViews
from sectors import views as sectorViews
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', loginViews.Login, name='login'),
    path('logout/', loginViews.Logout, name='logout'),
    path('register/', registerViews.Register, name='register'),
    path('dashboard/', loginViews.dashboard, name='dashboard'),
    path('profile/', loginViews.profile_view, name='profile'),
    path('event/<int:event_id>/', eventViews.event_detail, name='event_detail'),
    path('event/<int:event_id>/buy_ticket/', orderViews.buy_ticket, name='buy_ticket'),
    path('download_ticket/<int:order_id>/', orderViews.download_ticket, name='download_ticket'),
    path('show_ticket/<int:order_id>/', orderViews.show_ticket, name='show_ticket'),
    path('statistics/', eventViews.statistics, name='statistics'),
    path('', lambda request: redirect('login')),
    path('get-rows/', rowViews.get_rows, name='get_rows'),
    path('get-seats/', seatViews.get_seats, name='get_seats'),
    path('get-sectors/<int:event_id>/', sectorViews.get_sectors, name='get_sectors'),
    path('create-checkout-session/', orderViews.create_checkout_session, name='create-checkout-session'),
    path('checkout-success/', orderViews.checkout_success, name='checkout-success'),
    path('checkout-cancel/', orderViews.checkout_cancel, name='checkout-cancel'),
    path('get-sectors-admin/', sectorViews.get_sectors_admin, name='get_sectors_admin'),
    path('get-rows-admin/', rowViews.get_rows_admin, name='get_rows_admin'),
    path('add-multiple-rows/', rowViews.add_multiple_rows, name='add_multiple_rows'),
    path('statistics/', eventViews.statistics, name='statistics'),
    path('clear_cart/', orderViews.clear_cart, name='clear_cart'),
    path('cart/', orderViews.cart, name='cart'),
    path('remove-from-cart/<int:item_id>/', orderViews.remove_from_cart, name='remove_from_cart'),
    path('clear-expired-items/', orderViews.clear_expired_items, name='clear_expired_items'),
    path('add-to-cart/<int:event_id>/<int:seat_id>/<str:ticket_category>/<str:ticket_price>/', orderViews.add_to_cart, name='add_to_cart'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
