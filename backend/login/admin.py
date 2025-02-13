from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('email','passwordHash')

admin.site.register(User,UserAdmin)