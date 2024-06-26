"""Tests for the ingredients API"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Create and return an ingredient detail URL"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email="user@example.com", password="testpass123"):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


def create_ingredient(user, **params):
    """Create and return a sample ingredient."""
    defaults = {
        'name': 'sample name',
    }
    defaults.update(params)

    ingredient = Ingredient.objects.create(user=user, **defaults)
    return ingredient


class PublicIngredientApiTest(TestCase):
    """Tests for unauthenticated Ingredients API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """Tests for authenticated Ingredients API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients"""
        create_ingredient(self.user, name="Flour")
        create_ingredient(self.user, name="Water")

        res = self.client.get(INGREDIENT_URL)

        ingredient = Ingredient.objects.all().order_by('name')
        serializer = IngredientSerializer(ingredient, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_list_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user"""
        other_user = create_user(
            email="user2@example.com", password="pass1235")

        create_ingredient(other_user, name="Other user ingredient")
        ingredient = create_ingredient(self.user, name="My ingredient")

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_update_ingredient(self):
        """Test full update of a ingredient"""
        ingredient = create_ingredient(
            user=self.user,
            name="Sugar",
        )

        payload = {
            'name': "Powdered Sugar",
        }
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        ingredient.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.user, self.user)
        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredient(self):
        """Test deleting a ingredient succesfully"""
        ingredient = create_ingredient(
            user=self.user,
            name="Ingredient to delete",
        )

        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(id=ingredient.id)
        self.assertFalse(ingredients.exists())
