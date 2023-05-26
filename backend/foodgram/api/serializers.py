from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from recipes.models import IngredientRecipe, Favorite, Ingredient, Recipe, Tag
from rest_framework.serializers import (CharField, CurrentUserDefault,
                                        HiddenField, IntegerField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField, Serializer,
                                        SerializerMethodField)
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from users.models import Subscription, User
from recipes.models import ShoppingCart


class BaseUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password'
        )


class BaseUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return not user.is_anonymous and Subscription.objects.filter(
            user=user,
            author=obj
        ).exists()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class PasswordSerializer(Serializer):
    new_password = CharField(required=True)
    current_password = CharField(required=True)


class SubscriptionRecipeSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=obj, author=user).exists()

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipe_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = obj.recipes.all[:int(limit)]
        return SubscriptionRecipeSerializer(
            recipes,
            many=True,
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        author = self.instance
        method = request.method

        if method == 'POST':
            if user == author:
                raise ValidationError("You cannot subscribe to yourself.")

        if method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user,
                author=author
            )
            if not subscription.exists():
                raise ValidationError("You are not subscribed to this user.")

        return attrs

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )


class IngredientRecipeListSerializer(ModelSerializer):
    id = IntegerField(source='ingredient.id')
    name = CharField(
        source='ingredient.name'
    )
    measurement_unit = CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class IngredientRecipeCreateSerializer(ModelSerializer):
    id = IntegerField(write_only=True)
    amount = IntegerField(write_only=True)

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'amount',
        )


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class FavoriteSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(read_only=True)
    recipe = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')


class RecipeListSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    author = BaseUserSerializer()
    ingredients = IngredientRecipeListSerializer(many=True,
                                                 source='ingredient_recipe')
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return not user.is_anonymous and Favorite.objects.filter(
            user=user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(shopping_cart__user=user,
                                     id=obj.id).exists()

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        recipe = attrs['recipe']

        if request.method == 'POST':
            in_list = Recipe.objects.filter(user=user, recipe=recipe)
            if in_list.exists():
                raise ValidationError('Рецепт уже находится в списке покупок')

        if request.method == 'DELETE':
            in_list = Recipe.objects.filter(user=user, recipe=recipe)
            if not in_list.exists():
                raise ValidationError('Рецепта нет в списке')

        return attrs

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipeCreateSerializer(ModelSerializer):
    ingredients = IngredientRecipeCreateSerializer(many=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    author = HiddenField(default=CurrentUserDefault())

    def _add_ingredients(self, recipe, ingredients_data):
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(ingredient=get_object_or_404(
                Ingredient, id=ingredient_item.get('id')),
                recipe=recipe,
                amount=ingredient_item.get(
                    'amount')) for ingredient_item in ingredients_data]
        )

    def get_ingredients(self, obj):
        ingredients = obj.ingredient_recipes.all()
        return IngredientRecipeListSerializer(ingredients).data

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._add_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        instance.tags.clear()
        instance.ingredients.clear()
        for tag in tags_data:
            tag_id = tag.id
            tag_object = get_object_or_404(Tag, id=tag_id)
            instance.tags.add(tag_object)
        self._add_ingredients(instance, ingredients_data)
        return instance

    def validate(self, attrs):
        ingredients_data = attrs.get('ingredients')
        if ingredients_data:
            ingredient_ids = [ingredient.get('id')
                              for ingredient
                              in ingredients_data
                              ]
            amount = len(ingredient_ids)

            existing_recipe = Recipe.objects.filter(
                ingredient_recipe__ingredient_id__in=ingredient_ids,
                ingredient_recipe__amount=amount
            ).first()

            if existing_recipe:
                raise ValidationError(
                    'Рецепт с такими ингредиентами уже существует.'
                )
        return attrs

    def to_representation(self, instance):
        serializer = RecipeListSerializer(
            instance,
            context=self.context
        )
        return serializer.data

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author',
        )


class ShoppingCartSerializer(ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже находится в корзине'
            )
        ]
