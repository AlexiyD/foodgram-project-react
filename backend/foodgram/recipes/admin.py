from django.contrib import admin
from recipes.models import (IngredientRecipe, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)
    search_fields = ('name', 'slug',)
    ordering = ('color', )
    empty_value_display = '-пусто-'


class IngredientRecipeInLine(admin.TabularInline):
    model = IngredientRecipe


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('^name', )
    list_filter = ('name', )
    inlines = (IngredientRecipeInLine, )
    empty_value_display = '-пусто-'


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount',)
    list_filter = ('ingredient', 'recipe', 'amount')
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorited')
    list_filter = ('name', 'author', 'tags',)
    search_fields = ('name', 'author', 'tags',)
    inlines = (IngredientRecipeInLine, )
    empty_value_display = '-пусто-'

    def favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    favorited.short_description = 'В избранном'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
