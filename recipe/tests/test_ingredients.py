from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

class PublicIngredientsApiTests(TestCase):
    """ Probar API ingredientes accesibles publicamente """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Probar que el login es necesario para acceder este endpoint """
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsApiTests(TestCase):
    """ Probar API ingredientes accesibles privado """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """ Probar obtener lista de ingredientes """
        Ingredient.objects.create(user=self.user, name='milk')
        Ingredient.objects.create(user=self.user, name='Cheese')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """ Probar retornar ingredientes solamante autenticados por el usuario """
        self.user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'DataScience2021'
        )

        Ingredient.objects.create(user=self.user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='tumeric')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)


