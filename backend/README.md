# CoTask Backend

## Стек
* Python
* FastAPI
* PostgreSQL
* Docker

## Swagger (Endpoints)
![swagger.png](/assets/img/swagger.png)

* Стандартная аутентификация с JWT
* CREATE, READ, UPDATE пользователя
* Получение задач на весь проект, на команду, на одного человека
* Обновление информации о задаче
* Получение доступных команд и проектов
* Парсинг excel-файла

----------------

Приложение полностью упаковано в docker для удобного деплоя на сервер. Поэтому запуск просто:

```shell
docker-compose up
```
