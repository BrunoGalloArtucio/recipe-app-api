"""Serializers for recipe APIs"""
from rest_framework import serializers
from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        """Meta class for serializer"""
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        """Meta class for serializer"""
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']

    def get_or_create_tags(self, tags, recipe):
        """Get or create tags"""
        for tag in tags:
            # Destructuring get_or_create returned Tuple
            tag_obj, _ = Tag.objects.get_or_create(
                user=self.context['request'].user,
                **tag
            )
            recipe.tags.add(tag_obj)

    def create(self, validated_data):
        """Create a recipe"""
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        self.get_or_create_tags(tags, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self.get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        """Meta class for serializer"""
        fields = RecipeSerializer.Meta.fields + ['description']
