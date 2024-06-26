"""Tests for the tags API"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

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
