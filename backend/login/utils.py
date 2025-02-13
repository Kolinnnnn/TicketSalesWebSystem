import jwt
from django.shortcuts import redirect
from django.conf import settings
from functools import wraps
from login.models import User

def jwt_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get('auth_token')

        if not token:
            return redirect('login')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            user_id = payload.get('id')
            user = User.objects.get(id=user_id)
            
            request.user = user
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return _wrapped_view
