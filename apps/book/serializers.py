from django.db import IntegrityError

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from apps.book.models import Book,Favorite,Review
from apps.user.serializers import UserSerializer


class BookSerializer(serializers.ModelSerializer):
    created_by= UserSerializer(read_only=True)
    class Meta:
        model = Book
        fields = (
                'id',
                'title',
                'author',
                'description', 
                'is_active',
                'created_by'
                )
        read_only_fields = ('pdf_file','created_at', 'updated_at',)
        
    #  create method to set the created_by field to the current user
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if instance.created_by != self.context['request'].user:
            raise PermissionDenied("You do not have permission to update this book.")
        return super().update(instance, validated_data)
   

#Favorite book serializer
class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'book']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'You have already added this book to your favorite list.'})


class FavoriteBookSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Favorite
        fields = ['book']



#Rewiew
class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True)

    class Meta:
        model = Review
        fields = ('id', 'review_text', 'rating', 'user', 'book')

    def validate_rating(self, value):
        if value > 5 or value < 1:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        review = Review.objects.create(**validated_data)
        return review
