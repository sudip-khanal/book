from django.contrib import admin

# Register your models here.
from apps.user.models import CustomUser

class UserAdmin(admin.ModelAdmin):
    list_display=('id','username','email','is_active','phone_number','address','date_of_birth')
    
admin.site.register(CustomUser,UserAdmin)