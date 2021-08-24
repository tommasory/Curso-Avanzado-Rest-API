from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """ Serializador para el objeto de usuarios """

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        # Execiones
        extra_kwargs = {
            # Con esto protejemos la contraseña a la hora de retorno
            'password':{
                'write_only':True,# La clave se muestra solo cuando estamos creando
                'min_length':5,
                'style':{'input_type':'password'} # Mostrar asterisco y no los datos a la hora de crear.
            }
        }

    def create(self, validated_date):
        """ Crear nuevo usuario con clave encriptada y retornarla """
        return get_user_model().objects.create_user(**validated_date)

class AuthTokenSerializer(serializers.Serializer):
    """ Serializador para el objeto de autenticación de usuario """

    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},# Al escribir la contraseña aparesca cifrada
        trim_whitespace=False # Por si la contraseña tiene espacios los cuente
    )

    def validate(self, attrs):
        """ Validar y auntenticar usuario """
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username = email,# Porque nos estamos auntenticando con email
            password = password
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
