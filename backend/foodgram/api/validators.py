from rest_framework.exceptions import ValidationError


def validate_subscribe(user, author):
    if user == author:
        raise ValidationError("You cannot subscribe to yourself.")

def validate_unsubscribe(subscription):
    if not subscription.exists():
        raise ValidationError("You are not subscribed to this user.")
    
def validate_recipe_in_list(in_list):
    if in_list:
        raise ValidationError('Рецепт уже находится в списке покупок')

def validate_recipe_not_in_list(in_list):
    if not in_list:
        raise ValidationError('Рецепта нет в списке')