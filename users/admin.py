aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaafrom django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User 

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'points', 'is_staff')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Dodatkowe Informacje', {'fields': ('role', 'country', 'points', 'premium')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Dodatkowe Informacje', {'fields': ('role', 'country', 'points', 'premium')}),
    )

admin.site.register(User, CustomUserAdmin)