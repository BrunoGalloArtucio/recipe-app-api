"""Django admin customization"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models
# Good practice to use translation
from django.utils.translation import gettext_lazy as _


# This class defines the information shown about users in admin page
class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    # Only show email and name in page
    list_display = ['email', 'name']

    fieldsets = (
        # Title
        (None, {'fields': ('email', 'password')}),
        (
            # Translate
            _('Permissions'),
            {
                'fields': (
                    "is_active",
                    "is_staff",
                    'is_superuser'
                )
            }
        ),
        (
            # Translate
            _('Important dates'),
            {
                'fields': (
                    "last_login",
                )
            }
        ),
    )

    # Prevents users from modifying last_login in admin page
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )


# If we don't incldue UserAdmin here (it's optional param),
# then the default behavior would be to use the default model
# manager with the CRUD operations
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)
