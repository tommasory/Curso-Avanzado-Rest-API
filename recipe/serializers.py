from django.db.models import fields
from django.db.models.query import QuerySet
from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe

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

class RecipeSerializer(serializers.ModelSerializer):
    """ Serializa las Recetas """

    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset = Ingredient.objects.all()
    )

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset = Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'title', 'ingredients', 'tags', 'time_minutes', 'price',
            'link',
        )
        read_only_fields = ('id', )
