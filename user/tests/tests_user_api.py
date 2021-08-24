from django.test import TestCase,Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

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
            'password':'pw',
            'name':'Test name'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertAlmostEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ Probar que el token sea creado por el usuario """
        payload = {
            'email':'test@gmail.com',
            'password':'DataScience2021',
            'name':'Test name'
        }

        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """ Probar que el token no es creado con credenciales invalidas """

        create_user(email='test@gmail.com',password='DataScience2021')
        payload = {
            'email':'test@gmail.com',
            'password':'unicauca'
        }
        
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """ Prueba que no se crea token si no existe el usuario """
        payload = {
            'email':'test@gmail.com',
            'password':'DataScience2021',
            'name':'Test name'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """ Probar que el email y contraseña sean requeridos """
        res = self.client.post(TOKEN_URL, {'email':'test@','password':''})
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    
