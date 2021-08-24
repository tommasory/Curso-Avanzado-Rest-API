from .serializers import UserSerializer
from rest_framework import generics

class CreateUserView(generics.CreateAPIView):
    """ Crear nuevo usuario en el sistema """
    serializer_class = UserSerializer