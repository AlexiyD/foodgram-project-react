from django.conf import settings 
from django.core.validators import MaxValueValidator, MinValueValidator 
from .validators import validate_name, validate_color 
from django.db import models 
from django.db.models import (CASCADE, CharField, DateTimeField, ForeignKey, 
                              ImageField, ManyToManyField, 
                              PositiveSmallIntegerField, SlugField, TextField, 
                              UniqueConstraint) 
 
 
class Tag(models.Model): 
    name = CharField( 
        verbose_name='Тэг', 
        max_length=200, 
        unique=True, 
        validators=[validate_name] 
    ) 
 
    color = CharField( 
        verbose_name='Цвет', 
        max_length=7, 
        unique=True, 
        db_index=False, 
        validators=[validate_color] 
    ) 
 
    slug = SlugField( 
        verbose_name='Слаг тэга', 
        max_length=200, 
        unique=True, 
    ) 
 
    class Meta: 
        ordering = ('-id',) 
        verbose_name = 'Тэг' 
        verbose_name_plural = 'Теги' 
 
    def __str__(self): 
        return self.name 
 
 
class Ingredient(models.Model): 
    name = CharField( 
        verbose_name='Ингредиент', 
        max_length=200, 
    ) 
    measurement_unit = CharField( 
        verbose_name='Единица измерения', 
        max_length=200, 
    ) 
 
    class Meta: 
        verbose_name = 'Ингредиент' 
        verbose_name_plural = 'Ингредиенты' 
 
    def __str__(self): 
        return self.name 
 
 
class Recipe(models.Model): 
    ingredients = ManyToManyField( 
        verbose_name='Ингредиенты', 
        related_name='recipe', 
        to=Ingredient, 
        through='IngredientRecipe', 
    ) 
    tags = ManyToManyField( 
        Tag, 
        verbose_name='Тег', 
        related_name='recipe', 
    ) 
    image = ImageField( 
        verbose_name='Катринка', 
        upload_to='recipes/image/', 
    ) 
    name = CharField( 
        verbose_name='Название рецепта', 
        max_length=200, 
    ) 
    text = TextField( 
        verbose_name='Описание рецепта', 
    ) 
    cooking_time = PositiveSmallIntegerField( 
        validators=[ 
            MinValueValidator( 
                1, 
                message='время приготовления не должно быть < 1 мин.' 
            ), 
            MaxValueValidator( 
                10000, 
                message='время приготовления не должно быть > 10000 мин.' 
            ) 
        ], 
        verbose_name='Время приготовления рецепта', 
    ) 
    author = ForeignKey( 
        settings.AUTH_USER_MODEL, 
        on_delete=CASCADE, 
        null=True, 
        verbose_name='Автор', 
        related_name='recipes', 
    ) 
    pub_date = DateTimeField( 
        verbose_name='Дата', 
        auto_now_add=True, 
    ) 
 
    class Meta: 
        verbose_name = 'Рецепт' 
        verbose_name_plural = 'Рецепты' 
        ordering = ('-pub_date', ) 
 
    def __str__(self): 
        return f'{self.name} {self.author.username}' 
 
 
class IngredientRecipe(models.Model): 
    recipe = ForeignKey( 
        to=Recipe, 
        on_delete=CASCADE, 
        verbose_name='Рецепт', 
        related_name='ingredient_recipe' 
    ) 
    ingredient = ForeignKey( 
        to=Ingredient, 
        on_delete=CASCADE, 
        verbose_name='Ингредиент', 
        related_name='ingredient_recipe' 
    ) 
    amount = PositiveSmallIntegerField( 
        validators=[ 
            MinValueValidator(1, message='Добавте еще'), 
            MaxValueValidator(100, message='перебор'), 
        ], 
        verbose_name='Количество', 
    ) 
 
    class Meta: 
        constraints = [ 
            UniqueConstraint(fields=('recipe', 'ingredient'), 
                             name='unique_ingredient_recipe') 
        ] 
        ordering = ('id',) 
        verbose_name = 'Кол-во ингредиента' 
        verbose_name_plural = 'Кол-во ингредиента' 
 
    def __str__(self): 
        return f'{self.amount} {self.ingredient}' 
 
 
class Favorite(models.Model): 
    user = ForeignKey( 
        settings.AUTH_USER_MODEL, 
        on_delete=CASCADE, 
        verbose_name='Пользователь', 
        related_name='favorites', 
    ) 
    recipe = ForeignKey( 
        Recipe, 
        on_delete=CASCADE, 
        verbose_name='Избраный Рецепт', 
        related_name='favorites', 
    ) 
 
    class Meta: 
        ordering = ('id',) 
        verbose_name = 'Избранное' 
        verbose_name_plural = 'Избранные' 
 
    def __str__(self): 
        return f'{self.user} {self.recipe}' 
 
 
class ShoppingCart(models.Model): 
    recipe = ForeignKey( 
        Recipe, 
        on_delete=CASCADE, 
        verbose_name='Покупка', 
        related_name='shopping_cart' 
    ) 
    user = ForeignKey( 
        settings.AUTH_USER_MODEL, 
        on_delete=CASCADE, 
        verbose_name='Пользователь', 
        related_name='shopping_cart' 
    ) 
 
    class Meta: 
        constraints = [ 
            UniqueConstraint( 
                fields=('recipe', 'user'), 
                name='unique_cart' 
            ) 
        ] 
        ordering = ('id',) 
        verbose_name = 'Список покупок' 
        verbose_name_plural = 'Списки покупок' 
 
    def __str__(self): 
        return f'{self.recipe} в корзине у {self.user}' 
