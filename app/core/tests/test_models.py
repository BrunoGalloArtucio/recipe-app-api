"""Tests for models."""

# We use TestCase because we need db for these tests
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email successful."""
        email = "test@example.com"
        password = "testpassword123"
        user = get_user_model().objects.create_user(
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
            user = get_user_model().objects.create_user(
                email=test_case.get("email"),
                password=password
            )
            self.assertEqual(user.email, test_case.get("expected"))

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without email raises a ValueError."""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
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
