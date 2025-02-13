from .forms import RegisterForm
import bcrypt
from django.shortcuts import render, redirect
from login.models import User

def Register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            if User.objects.filter(email=email).exists():
                form.add_error(None, 'A user with this email already exists.')
            else:                
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                user = User(email=email, passwordHash=hashed_password.decode('utf-8'))
                user.save()

                return redirect('login')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})
