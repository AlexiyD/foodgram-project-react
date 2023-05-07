from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Follow

class UserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name',]
    list_filter = ['username', 'email']
    search_fields = ['username', 'email']
    ordering = ['email']

class FollowAdmin(admin.ModelAdminin):
    list_display = ('user', 'author')


admin.site.register(FollowAdmin)
admin.site.register(UserAdmin)