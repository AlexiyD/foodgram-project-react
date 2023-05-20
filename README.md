# praktikum_new_diplom
![example workflow](https://github.com/AlexiyD/foodgram-project-react/actions/workflows/yamdb_workflow.yml/badge.svg)
# Сайт Foodgam - Продуктовый помощник
## Описание:
>На этом сервисе пользователи смогут публиковать рецепты,
>подписываться на публикации других пользователей,
>добавлять понравившиеся рецепты в список «Избранное»,
>а перед походом в магазин скачивать сводный список продуктов,
>необходимых для приготовления одного или нескольких выбранных блюд.

### Технологии:
* Python 3.8 (https://docs.python.org/3.8/)
* Django 3.2.16 (https://docs.djangoproject.com/en/4.2/)
* Django REST framework 3.12.4 (https://www.django-rest-framework.org/community/release-notes/#release-notes)
* PyJWT + Djoser 2.1.0
* Djangorestframework-simplejwt 4.8.0 
* Docker (https://docs.docker.com/reference/)
* Nginx (https://hub.docker.com/_/nginx)
* Postgresql (https://www.postgresql.org/docs/)
* React

## структура приложения:
* В папке frontend - находятся файлы, необходимые для сборки фронтенда приложения.
* В папке infra - находится инфраструктура проекта: конфигурационный файл nginx и docker-compose.yml.
* В папке backend - файлы бэкенда продуктового помощника.
* В папке data подготовлен список ингредиентов с единицами измерения.
* В папке docs — файлы спецификации API.


## Как запустить проект:

### Клонировать репозиторий и перейти в него в командной строке:
* git clone 
https://github.com/AlexiyD/foodgram-project-react.git

### Перейти в рабочую дерикторию:
* cd .../foodgram-project-react

### Установить и активировать виртуальное окружение:
* python -m venv venv
* source venv/Scripts/activate

### Установить зависимости из файла requirements.txt:
* pip install -r requirements.txt

### Выполнить миграции, создать суперпользователя и собрать статику:
* docker-compose exec web python manage.py migrate
* docker-compose exec web python manage.py createsuperuser
* docker-compose exec web python manage.py collectstatic --no-input 

### Заполнить БД из дфмпа:
* docker-compose exec web python manage.py loaddata fixtures.json

### как заполнять файла .env:
* DB_ENGINE - БД 
* DB_NAME - имя БД
* POSTGRES_USER - имя пользователя БД
* POSTGRES_PASSWOR - пароль пользователя БД
* DB_HOST - адрес хоста с БД 
* DB_PORT - порт для подключения БД

* ip 158.160.11.67
## Автор:
* Зубков Алексей - AlexiyD (разработчик)