from django.contrib.auth import get_user_model
from django.test.utils import tag
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe import serializers

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

import tempfile
import os

from PIL import Image

RECIPES_URL = reverse('recipe:recipe-list')

def image_upload_url(recipe_id):
    """ URL de retorno para imagen subida """
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

def sample_tag(user, name='Main course'):
    """ Crea Tag de ejemplo """
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='Cinnamon'):
    """ Crea Ingrediente de ejemplo """
    return Ingredient.objects.create(user=user, name=name)

def detail_url(recipe_id):
    """ Retorna Receta Detail URL """
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_recipe(user, **params):
    """ Crear y retornar receta """
    defaults = {
        'title':'Sample recipe',
        'time_minutes':10,
        'price':5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)

class PublicRecipeApiTests(TestCase):
    """ Test acceso no autorizado al API """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """ Probar obtener lista de recetas """
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """ Probar obtener receta para un usuario """
        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'testpass'
        )

        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """ Prueba ver los detalles de una empresa """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """ Probar crear receta """
        payload = {
            'title':'Test recipe',
            'time_minutes':30,
            'price':10.00
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        
    def test_create_recipe_with_tags(self):
        """ Prueba crear recetas con Tag """
        tag1 = sample_tag(user=self.user, name='Tag 1')
        tag2 = sample_tag(user=self.user, name='Tag 2')
        payload = {
            'title':'Test recipe with two tags',
            'tags':[tag1.id, tag2.id],
            'time_minutes':30,
            'price':10.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """ Prueba crear recetas con Ingredientes"""
        ingredient1 = sample_ingredient(user=self.user, name='Ingredient 1')
        ingredient2 = sample_ingredient(user=self.user, name='Ingredient 2')
        payload = {
            'title':'Test recipe with two tags',
            'ingredients':[ingredient1.id, ingredient2.id],
            'time_minutes':30,
            'price':10.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)


class RecipeImageUploadTests(TestCase):
    """ Pruebas para la imagen """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user', 'testpass')
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        """ Elimina la imagen de la receta """
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """ Probar subir imagen a receta """
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image':ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """ Prueba de subir imagen fallida """
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image':'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        """ Test para filtrar recetas por tag """
        recipe1 = sample_recipe(user=self.user, title='Thai vegetable curry')
        recipe2 = sample_recipe(user=self.user, title='Aubergine with tahini')

        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Vegetarian')

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        recipe3 = sample_recipe(user=self.user, title='Fish and chips')

        res = self.client.get(
            RECIPES_URL,
            {'tags': '{},{}'.format(tag1.id, tag2.id)}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        """ Test para filtrar recetas por tag """
        recipe1 = sample_recipe(user=self.user, title='Thai vegetable curry')
        recipe2 = sample_recipe(user=self.user, title='Aubergine with tahini')

        ingredient1 = sample_ingredient(user=self.user, name='Vegan')
        ingredient2 = sample_ingredient(user=self.user, name='Vegetarian')

        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)

        recipe3 = sample_recipe(user=self.user, title='Fish and chips')

        res = self.client.get(
            RECIPES_URL,
            {'ingredients': '{},{}'.format(ingredient1.id, ingredient2.id)}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    