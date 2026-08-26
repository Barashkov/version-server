# Version Server

REST API сервис для управления версиями сервисов на различных площадках с веб-интерфейсом.

## 🏗️ Архитектура

Проект рефакторингирован с монолитной структуры в модульную архитектуру:

```
version-server/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Конфигурация через .env
│   ├── auth.py              # Общая аутентификация
│   ├── models/
│   │   └── schemas.py       # Pydantic модели для валидации
│   ├── routes/
│   │   ├── areas.py         # API endpoints для площадок
│   │   ├── services.py      # API endpoints для сервисов
│   │   └── web.py           # Web interface routes
│   ├── services/
│   │   └── data_manager.py  # Thread-safe управление данными
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Стили для web интерфейса
│   │   └── js/
│   │       └── app.js       # JavaScript для web интерфейса
│   ├── templates/
│   │   └── index.html       # HTML шаблон web интерфейса
│   └── utils/
│       └── logger.py        # Настройка логирования
├── tests/
│   ├── conftest.py          # pytest fixtures
│   ├── test_data_manager.py # Тесты data manager
│   └── test_api.py          # Тесты API endpoints
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.py                   # Точка входа
└── .env.example             # Пример конфигурации
```

## 🚀 Установка и запуск

### Локальная разработка

1. **Клонировать репозиторий**
   ```bash
   git clone https://github.com/Barashkov/version-server
   cd version-server
   ```

2. **Создать виртуальное окружение**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Установить зависимости**
   ```bash
   pip install -r requirements.txt
   ```

4. **Настроить переменные окружения**
   ```bash
   cp .env.example .env
   # Отредактировать .env с вашими настройками
   ```

5. **Запустить приложение**
   ```bash
   python run.py
   ```

### Docker

1. **Настроить переменные окружения**
   ```bash
   cp .env.example .env
   # Отредактировать .env с вашими настройками
   ```

2. **Запустить через docker-compose**
   ```bash
   docker-compose up -d
   ```

3. **Проверить статус**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

## ⚙️ Конфигурация

Все настройки управляются через переменные окружения в `.env` файле:

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `FLASK_ENV` | Режим работы (development/production) | `production` |
| `DEBUG` | Режим отладки | `False` |
| `HOST` | Хост для запуска | `0.0.0.0` |
| `PORT` | Порт | `5000` |
| `AUTH_USERNAME` | Имя пользователя для HTTP Basic Auth | `admin` |
| `AUTH_PASSWORD` | Пароль для HTTP Basic Auth | `admin` |
| `DATA_FILE` | Путь к файлу с данными | `services.json` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |

## 📡 API Endpoints

### Аутентификация

Все endpoints требуют HTTP Basic Auth с credentials из `.env`.

### Площадки (Areas)

#### Получить все площадки
```http
GET /api/v1.0/areas
```

#### Создать площадку
```http
POST /api/v1.0/area/{area_name}
```

#### Удалить площадку
```http
DELETE /api/v1.0/area/{area_name}
```

#### Обновить площадку
```http
PUT /api/v1.0/area/{area_name}
Content-Type: application/json

{
  "area_name": [
    {
      "id": 1,
      "name": "service1",
      "type": "web",
      "url": "http://example.com",
      "version": "1.0",
      "status": "active"
    }
  ]
}
```

### Сервисы (Services)

#### Получить все сервисы
```http
GET /api/v1.0/services
```

#### Получить сервисы площадки
```http
GET /api/v1.0/services/{area_name}
```

#### Получить сервис по ID
```http
GET /api/v1.0/services/{area_name}/{service_id}
```

#### Создать сервис
```http
POST /api/v1.0/services/{area_name}
Content-Type: application/json

{
  "name": "service_name",
  "type": "web",
  "url": "http://example.com",
  "version": "1.0",
  "status": "active"
}
```

#### Обновить сервис
```http
PUT /api/v1.0/services/{area_name}/{service_id}
Content-Type: application/json

{
  "version": "2.0",
  "status": "inactive"
}
```

#### Удалить сервис
```http
DELETE /api/v1.0/services/{area_name}/{service_id}
```

## 🧪 Тестирование

### Запустить все тесты
```bash
pytest
```

### Запустить с покрытием
```bash
pytest --cov=app --cov-report=html
```

### Запустить конкретный тест
```bash
pytest tests/test_data_manager.py::TestDataManager::test_create_area
```

## 🔒 Безопасность

- **HTTP Basic Auth** - все endpoints защищены базовой аутентификацией
- **Thread-safe операции** - DataManager использует блокировки для предотвращения race conditions
- **Валидация данных** - Pydantic модели для валидации входных данных
- **Логирование** - все операции логируются для аудита
- **Non-root Docker user** - контейнер запускается от имени непривилегированного пользователя

## 📝 Swagger Documentation

После запуска приложения доступна автоматическая документация API:

```
http://localhost:5000/apidocs/
```

## 🌐 Web Interface

После запуска приложения доступен веб-интерфейс для управления сервисами:

```
http://localhost:5000/
```

### Возможности веб-интерфейса:

- **Управление площадками**: создание, просмотр и удаление площадок
- **Управление сервисами**: создание, редактирование и удаление сервисов
- **Интерактивный интерфейс**: современный дизайн с уведомлениями и модальными окнами
- **Аутентификация**: те же credentials, что и для API

### Функции веб-интерфейса:

1. **Вкладка "Площадки"**:
   - Просмотр списка всех площадок
   - Создание новых площадок
   - Удаление площадок с сервисами
   - Быстрый переход к сервисам площадки

2. **Вкладка "Сервисы"**:
   - Выбор площадки для просмотра сервисов
   - Создание новых сервисов с валидацией
   - Редактирование существующих сервисов
   - Удаление сервисов
   - Просмотр детальной информации о сервисах

## 📚 Дальнейшие улучшения

1. **База данных** - рассмотреть замену JSON на SQLite/PostgreSQL
2. **Async operations** - переход на async/await для длительных операций
3. **Rate limiting** - добавить ограничение запросов
4. **Caching** - добавить кэширование для часто запрашиваемых данных
5. **Monitoring** - интеграция с Prometheus/Grafana
6. **CI/CD** - настройка автоматического тестирования и деплоя
7. **API versioning** - улучшенная поддержка версионирования API

## 📄 Лицензия

MIT

## 👥 Авторы

barashkovu@gmail.com
