from django.test import TestCase,Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """ Testar el API publica de Usuario """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """ Probar crear un usuario con un Payload exitoso """
        payload = {
            'email':'test@gmail.com',
            'password':'DataScience2021',
            'name':'Test name'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertAlmostEqual(res.status_code, status.HTTP_201_CREATED)
        # LLenamos el objeto con la respuesta
        user = get_user_model().objects.get(**res.data)
        # Comparamo que el objeto tenga la misma contraseña del payload
        self.assertTrue(user.check_password(payload['password']))
        # Que en la respuesta no esta la contraseña
        self.assertNotIn('password', res.data)

    def test_user_exist(self):
        """ Probar crear un usuario que ya existe falla """
        payload = {
            'email':'test@gmail.com',
            'password':'DataScience2021',
            'name':'Test name'
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertAlmostEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ La contraseña debe ser mayor a 5 caracteres """
        payload = {
            'email':'test@gmail.com',
            'password':'pw'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertAlmostEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)