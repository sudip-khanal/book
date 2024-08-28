from django.db import models

from apps.user.models import CustomUser

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200) 
    description = models.TextField(max_length=500)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# Model representing a user's favorite book
class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    #  a user can not favorite the same book more than once
    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.book.title}"


# review model
class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    review_text = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Review  book: {self.book}"

