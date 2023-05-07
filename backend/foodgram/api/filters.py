from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe, Tag, Ingredient
from django.db.models import BooleanField, ExpressionWrapper, F


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all())
    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite_recipe__user=user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_recipe__user=user)
        return queryset
    

class IngredientFilter(FilterSet):
    """Фильтр ингредиентов по названию"""
    name = filters.CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def filter_name(self, queryset, name, value):
        """Метод возвращает кверисет с заданным именем ингредиента."""
        return queryset.filter(
            F(name__istartswith=value) | F(name__icontains=value)
        ).annotate(
            startswith=ExpressionWrapper(
                F(name__istartswith=value),
                output_field=BooleanField()
            )
        ).order_by('-startswith')