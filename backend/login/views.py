from .forms import LoginForm
from .models import User
import bcrypt
import jwt
from django.utils import timezone
from django.shortcuts import render, redirect
from django.conf import settings
from .utils import jwt_required
from events.models import Event
from orders.models import Order


@jwt_required
def dashboard(request):
    user_email = request.user.email.split('@')[0]
    events = Event.objects.filter(start__gte=timezone.now())
    return render(request, 'home.html', {'events': events,'username': user_email})

def Login(request):
    if (request.method == 'POST'):
        form = LoginForm(request.POST)
        if (form.is_valid()):
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            try:
                user = User.objects.get(email = email)
                if bcrypt.checkpw(password.encode('utf-8'), user.passwordHash.encode('utf-8')):
                    token = jwt.encode({
                        'id':user.id,
                        'exp': timezone.now() + timezone.timedelta(hours=5)
                    },settings.SECRET_KEY, algorithm='HS256')                    
                    request.session['user_id'] = user.id
                    response = redirect('dashboard')
                    
                    if user.email == 'statistics@gmail.com':
                        response = redirect('statistics')

                    response.set_cookie('auth_token',token,httponly=True)
                    return response
                else :
                    form.add_error(None, 'Invalid Email or Password')
            except User.DoesNotExist:
                form.add_error(None, 'Invalid Email or Password')
    else: 
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def Logout(request):
    response = redirect('login')
    response.delete_cookie('auth_token')
    return response

@jwt_required
def profile_view(request):
    user_id = request.user.id
    try:
        user_instance = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return render(request, 'profile.html', {'orders': [], 'error': 'User does not exist.'})

    orders = Order.objects.filter(user=user_instance)

    return render(request, 'profile.html', {'orders': orders})