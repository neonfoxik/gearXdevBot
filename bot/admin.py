from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'user_tg_name', 'user_name', 'is_admin')
    search_fields = ('user_name', 'user_tg_name', 'telegram_id')
    list_filter = ('is_admin',)
    ordering = ('user_name',)

admin.site.register(User, UserAdmin)
