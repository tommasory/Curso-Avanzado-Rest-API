from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializers

TAGS_URL = reverse('recipe:tag-list')

class PublicTagsApiTests(TestCase):
    """ Probar los API tags disponible publicamente """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Prueba que login sea requerido para optener los tags """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsApiTests(TestCase):
    """ Probar los API tags disponibles privados """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'DataScience2021'
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """ Probar optener tags """
        Tag.objects.create(user=self.user, name='Meat')
        Tag.objects.create(user=self.user, name='Banana')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializers(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ Probar que los tags sean del usuario """
        self.user2 = get_user_model().objects.create_user(
            'otro@gmail.com',
            'DataScience2021'
        )

        Tag.objects.create(user=self.user2, name='Samsun')
        tag = Tag.objects.create(user=self.user, name='comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """ Prueba creando nuevo tag """
        payload = {'name':'Simple'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """ Prueba crear un nuevo tag con un payload invalido """
        payload = {'name':''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

