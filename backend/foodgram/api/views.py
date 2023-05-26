from django.db.models import Sum
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (IngredientRecipe, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.validators import ValidationError
from users.models import Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (BaseUserSerializer, FavoriteSerializer,
                          IngredientSerializer, PasswordSerializer,
                          RecipeCreateSerializer, RecipeListSerializer,
                          ShoppingCartSerializer, SubscriptionSerializer,
                          TagSerializer)


class ListRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    pass


class SubscriptionPasswordUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = BaseUserSerializer

    @action(methods=['POST'],
            detail=False,
            permission_classes=[IsAuthenticated]
            )
    def set_password(self, request, pk=None):
        user = self.request.user
        serializer = PasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'],
            detail=False,
            permission_classes=[IsAuthenticated]
            )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=[IsAuthenticated]
            )
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(user=user, author=author)

        if request.method == 'POST':
            if subscription.exists():
                raise ValidationError('You cannot subscribe to yourself.')
            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(author,
                                                context={'request': request}
                                                )
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED
                            )

        if request.method == 'DELETE':
            if not subscription.exists():
                raise ValidationError('You are not subscribed to this user.')
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=[IsAuthenticated]
            )
    def favorite(self, request, pk=None):
        return self._add_or_remove_recipe_from_list(request,
                                                    pk,
                                                    FavoriteSerializer,
                                                    Favorite
                                                    )

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=[IsAuthenticated]
            )
    def shopping_cart(self, request, pk=None):
        return self._add_or_remove_recipe_from_list(request,
                                                    pk,
                                                    ShoppingCartSerializer,
                                                    ShoppingCart
                                                    )

    @action(methods=['GET'],
            detail=False,
            permission_classes=[IsAuthenticated]
            )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by().annotate(Sum('amount'))

        shopping_list = 'Shopping list:\n'
        for ingredient in ingredients:
            name, measure, amount = ingredient
            shopping_list += f'{name} ({measure}) — {amount}\n'

        response = HttpResponse(content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_list.txt"'
        response.write(shopping_list)

        return response

    def _add_or_remove_recipe_from_list(self,
                                        request,
                                        pk,
                                        serializer_class,
                                        list_model):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        in_list = list_model.objects.filter(user=user, recipe=recipe)

        if request.method == 'POST':
            if not in_list:
                list_objects = list_model.objects.create(user=user,
                                                         recipe=recipe
                                                         )
                serializer = serializer_class(list_objects)
                return Response(data=serializer.data,
                                status=status.HTTP_201_CREATED
                                )

            raise ValidationError('Рецепт уже находится в списке покупок')

        if request.method == 'DELETE':
            if not in_list:
                raise ValidationError('Рецепта нет в списке')

            in_list.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if self._recipe_already_exists(serializer.validated_data):
            raise ValidationError(
                'Рецепт с такими ингредиентами уже существует.'
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers
                        )

    def _recipe_already_exists(self, validated_data):
        ingredients_data = validated_data.get('ingredients')
        if ingredients_data:
            ingredient_ids = [ingredient.get('id')
                              for ingredient
                              in ingredients_data]
            amount = len(ingredient_ids)

            existing_recipe = Recipe.objects.filter(
                ingredient_recipe__ingredient_id__in=ingredient_ids,
                ingredient_recipe__amount=amount
            ).first()

            if existing_recipe:
                return True

        return False
