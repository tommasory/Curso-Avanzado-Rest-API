from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        """ Probar crear un nuevo usuario con un email correctamente """
        email = 'test@unicauca.edu.co'
        password = 'DataScience2021'

        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        
    def test_new_user_email_normalized(self):
        """ Test de email para nuevo usuario normalizado """
        email = 'test@UNICAUCA.EDU.CO'

        user = get_user_model().objects.create_user(email,'DataScience2021')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """ Nuevo usuario email invalidado """
        # Deberia validar que se levante una excepcion si no se pasa el email
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None,'DataScience2021')