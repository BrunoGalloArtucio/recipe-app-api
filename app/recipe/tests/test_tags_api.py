"""Tests for the tags API"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail URL"""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email="user@example.com", password="testpass123"):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


def create_tag(user, **params):
    """Create and return a sample tag."""
    defaults = {
        'name': 'sample name',
    }
    defaults.update(params)

    tag = Tag.objects.create(user=user, **defaults)
    return tag


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


class PublicTagApiTest(TestCase):
    """Tests for unauthenticated Tags API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTest(TestCase):
    """Tests for authenticated Tags API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags"""
        create_tag(self.user, name="Vegan")
        create_tag(self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_list_limited_to_user(self):
        """Test list of tags is limited to authenticated user"""
        other_user = create_user(
            email="user2@example.com", password="pass1235")

        create_tag(other_user)
        tag = create_tag(self.user)

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_update_tag(self):
        """Test full update of a tag"""
        tag = create_tag(
            user=self.user,
            name="Dinner",
        )

        payload = {
            'name': "After Dinner",
        }
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        tag.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.user, self.user)
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        """Test deleting a tag succesfully"""
        tag = create_tag(
            user=self.user,
            name="Tag to delete",
        )

        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(id=tag.id)
        self.assertFalse(tags.exists())

    def test_retrieve_assigned_only_tags(self):
        """Test retrieving only tags assigned to recipes"""
        recipe1 = create_recipe(user=self.user, title="Apple Crumble")
        tag1 = create_tag(self.user, name="Breakfast")
        tag2 = create_tag(self.user, name="Lunch")

        recipe1.tags.add(tag1)

        params = {'assigned_only': 1}
        res = self.client.get(TAGS_URL, params)

        serialized_tag1 = TagSerializer(tag1)
        serialized_tag2 = TagSerializer(tag2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serialized_tag1.data, res.data)
        self.assertNotIn(serialized_tag2.data, res.data)

    def test_assigned_tags_unique(self):
        """Test retrieving tags assigned to recipes does not
        return duplicates"""
        recipe1 = create_recipe(user=self.user, title="Apple Crumble")
        recipe2 = create_recipe(user=self.user, title="Apple Pie")

        tag1 = create_tag(self.user, name="Sweet")
        tag2 = create_tag(self.user, name="Sour")

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag1)

        params = {'assigned_only': 1}
        res = self.client.get(TAGS_URL, params)

        serialized_tag1 = TagSerializer(tag1)
        serialized_tag2 = TagSerializer(tag2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serialized_tag1.data, res.data)
        self.assertNotIn(serialized_tag2.data, res.data)
        self.assertEqual(len(res.data), 1)
