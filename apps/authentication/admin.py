from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, Role

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('name', 'email', 'phone_number', 'team')}),
        ('Permissions', {'fields': ('roles', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'name', 'email', 'password1', 'password2', 'roles', 'team', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'name')
    ordering = ('username',)
    def save_model(self, request, obj, form, change):
        if not change:
            # Save the user without roles first
            roles = form.cleaned_data.pop('roles', [])
            obj.save()
            # Add roles after saving the user
            for role_name in roles:
                role = Role.objects.create(name=role_name)
                obj.roles.add(role)
        else:
            obj.save()
            # Update roles if the user is being changed
            roles = form.cleaned_data.get('roles', [])
            obj.roles.clear()
            for role_name in roles:
                role = Role.objects.create(name=role_name)
                obj.roles.add(role)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Role)
