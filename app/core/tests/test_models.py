"""Tests for models."""

from unittest.mock import patch
from decimal import Decimal
# We use TestCase because we need db for these tests
from django.contrib.auth import get_user_model
from django.test import TestCase
from core import models


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email successful."""
        email = "test@example.com"
        password = "testpassword123"
        user = create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            {"email": 'test1@EXAMPLE.com', "expected": 'test1@example.com'},
            {"email": 'Test2@Example.com', "expected": 'Test2@example.com'},
            {"email": 'TEST3@EXAMPLE.COM', "expected": 'TEST3@example.com'},
            {"email": 'test4@example.COM', "expected": 'test4@example.com'},
        ]

        password = "testpassword123"

        for test_case in sample_emails:
            user = create_user(
                email=test_case.get("email"),
                password=password
            )
            self.assertEqual(user.email, test_case.get("expected"))

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without email raises a ValueError."""

        with self.assertRaises(ValueError):
            create_user(
                email='',
                password='password'
            )

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            email="test@example.com",
            password="testpassword123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful"""
        user = create_user(
            email="test@example.com",
            password="testpassword123"
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe name",
            time_minutes=5,
            price=Decimal('5.50'),
            description="Sample recipe description."
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful"""
        user = create_user(
            email="test@example.com",
            password="testpassword123"
        )

        tag = models.Tag.objects.create(
            user=user,
            name="Tag1"
        )

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating an ingredient is successful"""
        user = create_user(
            email="test@example.com",
            password="testpassword123"
        )

        ingredient = models.Ingredient.objects.create(
            user=user,
            name="Ingredient 1"
        )

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid

        user = create_user(
            email="test@example.com",
            password="testpassword123"
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe name",
            time_minutes=5,
            price=Decimal('5.50'),
            description="Sample recipe description."
        )

        file_path = models.recipe_image_file_path(recipe, 'example.jpg')

        self.assertEqual(file_path, f"uploads/recipe/{recipe.id}/{uuid}.jpg")
