
from django.contrib import admin

from apps.book.models import Book,Favorite,Review
"""
Register models in django admin using ModelAdmin which Encapsulate
all admin options and functionality for a given model.
"""
class BookAdmin(admin.ModelAdmin):
    list_display = ('id','title','author', 'created_by', 'description','is_active','created_at','updated_at')

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id','user','book')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id','book', 'user', 'review_text', 'rating','created_at')


admin.site.register( Book,BookAdmin)
admin.site.register( Favorite,FavoriteAdmin)
admin.site.register(Review,ReviewAdmin)
