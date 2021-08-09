from django.contrib import admin
from frontlinerapp.models import CustomUser
# Register your models here.

admin.site.register(CustomUser)

class CustomUserAdmin(admin.ModelAdmin):

    search_fields = ['email', ]
