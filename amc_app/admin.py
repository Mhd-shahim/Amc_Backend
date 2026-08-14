from django.contrib import admin
from .models import TblUsers


@admin.register(TblUsers)
class TblUsersAdmin(admin.ModelAdmin):
    list_display = (
        "id_user",
        "full_name",
        "email",
        "phone",
        "role",
        "is_active",
        "created_at",
        "last_login",
    )

    search_fields = (
        "full_name",
        "email",
        "phone",
    )

    list_filter = (
        "role",
        "is_active",
    )

    readonly_fields = (
        "id_user",
        "password_hash",
        "created_at",
        "last_login",
    )