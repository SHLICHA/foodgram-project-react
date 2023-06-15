# foodgram-project-react
### Ссылка на проект https://github.com/SHLICHA/foodgram-project-react.git

![workflow](https://github.com/shlicha/foodgram-project-react/actions/workflows/foodgram.yml/badge.svg)

## _Описание_

 «Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

# Самостоятельная регистрация новых пользователей

- Пользователь отправляет POST-запрос с параметрами email, username, password, first_name и last_name на эндпоинт /api/auth/signup/.

- В результате пользователь получает токен и может работать с API проекта, отправляя этот токен с каждым запросом.
 
- После регистрации и получения токена пользователь может отправить PATCH-запрос на эндпоинт /api/users/me/ и заполнить поля в своём профайле (описание полей — в документации).

> ВНИМАНИЕ!
> Если планируется использовать данный API в качестве промышленного,
> то необходимо убедиться, что в файле settings.py применены необходимые параметры:
> -- Отключен режим разработчика `DEBUG = False`
> -- В параметре `ALLOWED_HOSTS = []` заданы разрешенные адреса входящих соединений


> Полный перечень доступных в API методов содержится в `/api/docs/`

## _Установка_

1. Скопировать папки `docs` и `data` на сервер
2. Файлы `docker-compose.yml` и `nginx.conf` скопировать в тот же каталог на сервере
3. Создать файл .env со следующими данными:
  - DB_ENGINE=django.db.backends.postgresql
  - DB_NAME= `имя базы данных на сервере`
  - POSTGRES_USER= `имя пользователя базы данных`
  - POSTGRES_PASSWORD= `пароль пользователя базы данных`
  - DB_HOST=db
  - DB_PORT=5432 
4. Запустить команды: 
  - sudo docker-compose up -d
  - sudo docker-compose exec -T web python manage.py collectstatic --no-input
  - sudo docker-compose exec -T web python manage.py makemigrations
  - sudo docker-compose exec -T web python manage.py migrate
  - sudo docker-compose exec -T web python manage.py imports_csv data/ingredients.csv


Адрес сервера 51.250.85.145
Админка:
  - логин admin
  - пароль AdminYandex