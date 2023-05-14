from django.db.models import Sum
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

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
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

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
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

    @action(methods=['POST', 'DELETE'], detail=True, permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(user=user, author=author)
        if request.method == 'POST':
            if subscription.exists():
                data = {'data': 'You cannot subscribe to yourself.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(author, context={'request': request})
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not subscription.exists():
                data = {'data': 'You are not subscribed to this user.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
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

    @action(methods=['POST', 'DELETE'], detail=True, permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self._add_or_remove_recipe_from_list(request, pk, FavoriteSerializer, Favorite)

    @action(methods=['POST', 'DELETE'], detail=True, permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self._add_or_remove_recipe_from_list(request, pk, ShoppingCartSerializer, ShoppingCart)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(recipe__shopping_cart__user=request.user).values_list(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by().annotate(Sum('amount'))
        shopping_list = 'Shopping list:\n'
        for ingredient in ingredients:
            name, measure, amount = ingredient
            shopping_list += f'{name} ({measure}) — {amount}\n'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    def _add_or_remove_recipe_from_list(self, request, pk, serializer_class, list_model):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        in_list = list_model.objects.filter(user=user, recipe=recipe)

        if request.method == 'POST':
            if not in_list:
                list_objects = list_model.objects.create(user=user, recipe=recipe)
                serializer = serializer_class(list_objects.recipe)
                return Response(data=serializer.data, status=201)

        if request.method == 'DELETE':
            if not in_list:
                data = {'errors': 'Рецепта нет в списке'}
                return Response(data=data, status=400)
            in_list.delete()
            return Response(status=204)