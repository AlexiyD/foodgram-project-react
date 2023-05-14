from django.contrib import admin

from .models import Subscription, User

class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'password'
    )
    list_filter = ('email', 'username')
    search_fields = ('username', 'email', )
    empty_value_display = '-пусто-'

class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author'
    )
    search_fields = ('user', )
    list_filter = ('user', )
    empty_value_display = '-пусто-'

admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscribeAdmin)