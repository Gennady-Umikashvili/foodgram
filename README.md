http://158.160.30.10/

админка логин и пароль твои

# FOODGRAM

Foodgram - онлайн сервис для публикации рецептов.

## Возможности

Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.

## Infra

- Django
- Python
- Docker

## Запуск проекта:

1. Клонируйте проект:

```
git clone https://github.com/Gennady-Umikashvili/foodgram-project-react.git
```

2. Подготовьте сервер:

```
scp docker-compose.yml <username>@<host>:/home/<username>/
scp nginx.conf <username>@<host>:/home/<username>/
scp .env <username>@<host>:/home/<username>/
```

3. Установите docker и docker-compose:

```
sudo apt install docker.io 
sudo apt install docker-compose
```

4. Соберите контейнер и выполните миграции:

```
sudo docker-compose up -d --build
sudo docker-compose exec backend python manage.py migrate
```

5. Создайте суперюзера и соберите статику:

```
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input
```

6. Скопируйте предустановленные данные json:

```
sudo docker-compose exec backend python manage.py load_data --path 'recipes/data/tags.json'
docker-compose exec backend python manage.py load_data --path 'recipes/data/ingredients.json'
```

## Автор

https://github.com/Gennady-Umikashvili
