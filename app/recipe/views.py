"""Views for the recipe APIs"""

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Override get_queryset method to only return recipes created by the user
    # instead of returning all recipes which would be the default behavior
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    # Most of the methods we perform in the viewset use the detail serializer.
    # By default, we've included multiple methods like creating, updating and
    # deleting new items. All these use the detail serializer (we want to
    # include the description fields)
    def get_serializer_class(self):
        """Return the serializer class for a request"""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    # Override create Recipe to set self as creating user
    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

# This class is used to encapsulate all the duplicated logic
# between TagViewSet and IngredientViewSet


class BaseRecipeAttrViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Base view set for recipe attributes"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Create a new object for authenticated user"""
        serializer.save(user=self.request.user)

    # Override get_queryset method to only return objects created by the user
    # instead of returning all objects which would be the default behavior
    def get_queryset(self):
        """Retrieve objects for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('name')


class TagViewSet(BaseRecipeAttrViewSet):
    """View for manage tags APIs."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """View for manage ingredient APIs."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
