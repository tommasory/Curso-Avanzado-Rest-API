from django.db.models import fields
from rest_framework import serializers

from core.models import Tag, Ingredient

class TagSerializer(serializers.ModelSerializer):
    """ Serializador para objeto de Tag """

    class Meta:
        model  = Tag
        fields = ('id', 'name')
        read_only_Fields = ('id',)

class IngredientSerializer(serializers.ModelSerializer):
    """ Serializador para objeto de Ingredient """

    class Meta:
        model  = Ingredient
        fields = ('id', 'name')
        read_only_Fields = ('id',)