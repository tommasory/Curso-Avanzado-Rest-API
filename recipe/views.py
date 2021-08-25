from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient

from recipe import serializers

class BaseRecipeAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, 
                            mixins. CreateModelMixin):
    """ ViewSet Base """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """ Retornar objetos para el usuario autenticado """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """ Crear nuevo objeto """
        serializer.save(user=self.request.user)

class TagViewSet(BaseRecipeAttrViewSet):
    """ Manejar Tags en base de datos """
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

class IngredientViewSet(BaseRecipeAttrViewSet):
    """ Manejar Ingredientes en base de datos """
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
