from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Booking, Vehicle, Document
from django.utils.translation import gettext_lazy as _
from django import forms

# Custom UserCreationForm and UserChangeForm if you want to customize forms (optional)
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email',)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('service', 'date', 'time', 'status', 'user', 'vehicle', 'price')
    list_filter = ('status', 'date')
    search_fields = ('service', 'user__email', 'vehicle')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'registration', 'user', 'mileage', 'mot_expiry', 'last_service')
    search_fields = ('make', 'model', 'registration', 'user__email')
    list_filter = ('year',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('doc_type', 'date', 'vehicle', 'status', 'user')
    search_fields = ('doc_type', 'vehicle', 'user__email')
    list_filter = ('status',)
