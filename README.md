# foodgram-project-react

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




  

 
