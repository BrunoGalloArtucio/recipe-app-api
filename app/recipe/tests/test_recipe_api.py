"""Tests for recipe APIs."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer
)

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'sample recipe title',
        "time_minutes": 22,
        "price": Decimal('5.25'),
        "description": "sample description",
        "link": "https://example.com/recipe.pdf"
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_tag(user, **params):
    """Create and return a sample tag."""
    defaults = {
        'name': 'sample name',
    }
    defaults.update(params)

    tag = Tag.objects.create(user=user, **defaults)
    return tag


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTest(TestCase):
    """Tests for unauthenticated Recipe API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Tests for authenticated Recipe API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="user@example.com",
            password='testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(self.user)
        create_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user"""
        other_user = create_user(
            email="otheruser@example.com",
            password='testpass123'
        )

        create_recipe(other_user)
        create_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe"""
        payload = {
            'title': 'Sample recipe create',
            'time_minutes': 30,
            'price': Decimal('5.99')
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of a recipe"""
        original_link = "https://example.com/recipe.pdf"

        recipe = create_recipe(
            user=self.user,
            title="Sample recipe title",
            link=original_link
        )

        payload = {'title': "Updated title"}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of a recipe"""
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe title",
            link="https://example.com/recipe.pdf",
            description="Sample description"
        )

        payload = {
            'title': "Updated title",
            "link": "https://example.com/recipe-updated.pdf",
            'description': "Sample description new",
            'time_minutes': 10,
            'price': Decimal('2.50')
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.user, self.user)

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

    def test_update_user_returns_error(self):
        """Test changing the recipe user returns error"""
        new_user = create_user(email="user2@example.com", password="test123")
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe title",
            link="https://example.com/recipe.pdf"
        )

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe succesfully"""
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe title",
            link="https://example.com/recipe.pdf"
        )

        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id))

    def test_delete_other_users_recipe(self):
        """Test deleting another user's recipe returns error"""
        new_user = create_user(email="user2@example.com", password="test123")
        recipe = create_recipe(
            user=new_user,
            title="Sample recipe title",
            link="https://example.com/recipe.pdf"
        )

        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id))

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags"""
        payload = {
            'title': "Recipe with tags",
            "link": "https://example.com/recipe-updated.pdf",
            'description': "Sample description",
            'time_minutes': 10,
            'price': Decimal('2.50'),
            'tags': [
                {'name': 'Tag 1'},
                {'name': 'Tag 2'},
            ]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tags"""
        existing_tag = create_tag(self.user, name="Existing tag")
        payload = {
            'title': "Recipe with tags",
            "link": "https://example.com/recipe-updated.pdf",
            'description': "Sample description",
            'time_minutes': 10,
            'price': Decimal('2.50'),
            'tags': [
                {'name': existing_tag.name},
                {'name': 'Tag 2'},
            ]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(existing_tag, recipe.tags.all())

        for payload_tag in payload['tags']:
            exists = recipe.tags.filter(
                name=payload_tag['name'], user=self.user
            ).exists()
            self.assertTrue(exists)

        tags = Tag.objects.filter(user=self.user)
        self.assertEqual(tags.count(), 2)

    def test_create_tag_on_update(self):
        """Test creating tags when updating recipes"""
        tag_name = 'Tag 1'
        recipe = create_recipe(self.user)

        payload = {
            'tags': [
                {'name': tag_name},
            ]
        }
        res = self.client.patch(detail_url(recipe.id), payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        created_tag = Tag.objects.get(user=self.user, name=tag_name)
        # no need to recipe.refresh_from_db() because recipe.tags.all() does a
        # new query since it's a many-to-many field
        self.assertIn(created_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning existing tag and removing previous tag when updating recipe"""
        existing_tag = create_tag(self.user, name="Existing Tag 1")
        existing_tag_2 = create_tag(self.user, name="Existing Tag 2")
        recipe = create_recipe(self.user)
        recipe.tags.add(existing_tag_2)

        payload = {
            'tags': [
                {'name': existing_tag.name},
            ]
        }
        res = self.client.patch(detail_url(recipe.id), payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # no need to recipe.refresh_from_db() because recipe.tags.all() does a
        # new query since it's a many-to-many field
        recipe_tags = recipe.tags.all()
        self.assertIn(existing_tag, recipe_tags)
        self.assertNotIn(existing_tag_2, recipe_tags)

    def test_clear_recipe_tag(self):
        """Test clearing recipes tags"""
        existing_tag = create_tag(self.user)
        existing_tag_2 = create_tag(self.user)
        recipe = create_recipe(self.user)
        recipe.tags.add(existing_tag)
        recipe.tags.add(existing_tag_2)

        payload = {
            'tags': []
        }
        res = self.client.patch(detail_url(recipe.id), payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # no need to recipe.refresh_from_db() because recipe.tags does a
        # new query since it's a many-to-many field
        self.assertEqual(recipe.tags.count(), 0)
