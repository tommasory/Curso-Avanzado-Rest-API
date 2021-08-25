from django.db.models import fields
from rest_framework import serializers

from core.models import Tag

class TagSerializers(serializers.ModelSerializer):
    """ Serializador para objeto de Tag """

    class Meta:
        model  = Tag
        fields = ('id', 'name')
        read_only_Fields = ('id',)