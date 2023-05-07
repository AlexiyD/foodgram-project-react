from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import UniqueConstraint
User = get_user_model()

class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True, 
        verbose_name='Название', 
        help_text='Название тега',
    )
    color = models.CharField(
        max_length=7, 
        default='#00ff7f',
        null=True,
        blank=True, 
        unique=True,
        verbose_name='color HEX-code',
        help_text='color HEX-code',
    )
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
    


class Ingredient(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название ингредиента',
        help_text='Название ингредиента',
    )
    unit = models.CharField(
        max_length=50,
        verbose_name='Единица измерения', 
        help_text='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации',
        help_text='Автор рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='название',
        help_text='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='фото',
        help_text='Фото блюда'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='Recipes',
        verbose_name='Ингредиенты',
        help_text='Ингредиенты рецепта',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание рецепта',
    )
    tags = models.ManyToManyField(
        'Tag', 
        related_name='recipes',
        verbose_name = 'Тег',
        verbose_name_plural = 'Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(MinValueValidator(
            limit_value=1,
            message='Убедитесь, что время приготовление больше 1 мин!'),
        )
    )
    pub_date = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        
    def __str__(self):
        return self.name



    

class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='RecipeIngredien',
        verbose_name='Ингредиент',
        help_text='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='RecipeIngredien',
        verbose_name='Рецепт',
        help_text='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1, 'нужно добавить ингредиент!'
            ),
            MaxValueValidator(
                500, 'привышен лимит ингредиентов!'
            )
        ],
        default=1,
        verbose_name='Количество',
        help_text='Количество',
    )

    class Meta:
        verbose_name = 'Кол-во ингредиентов'
        verbose_name_plural = 'Кол-во ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe',
            )
        ]

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
        help_text='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Избранный автор',
        help_text='Избранный автор',
    )

    class Meta:
        verbose_name = 'Избранный автор'
        verbose_name_plural = 'Избранные авторы'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_relationships'
            ),
            models.CheckConstraint(
                name='prevent_self_follow',
                check=~models.Q(user=models.F('author')),
            ),
        ]

    def __str__(self):
        return f'{self.user} {self.author}'
    

class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique favorite'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shoppingcart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='shoppingcart'
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique recipe in shopping cart'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в корзине у {self.user}'