# FastAPI

Описание API:

Создание / удаление / изменение / получение информации по короткой ссылке:

POST /links/shorten – создает короткую ссылку 
**payload (body):** 
original_url: HttpUrl
custom_alias: Optional[str] = None
expires_at: Optional[datetime] = None).

Пример:
Request:
{
  "original_url": "https://example1.com/",
  "custom_alias": "string123",
  "expires_at": "2026-03-15T20:02:46.289Z"
}
Response:
Response body
{
  "short_code": "string123",
  "original_url": "https://example1.com/"
}

GET /links/{short_code} – перенаправляет на оригинальный URL.
**query (PATH)**:
short_code: str

Пример:
Request:
GET \ http://localhost:8000/api/links/string123

Response:
{
  "original_url": "https://example1.com/"
}

DELETE /links/{short_code} – удаляет связь.
**query (PATH)**:
short_code: str

Пример:
Request:
DELETE \ http://localhost:8000/api/links/string123

Response:
{
  "detail": "Ссылка удалена"
}

PUT /links/{short_code} – обновляет URL (То есть, короткий адрес. Будем засчитывать и другую реализацию - когда к короткой ссылке привязывается новая длинная).
**query (PATH)**:
short_code: str
**payload (body):** 
original_url: HttpUrl

Пример:
Request:
PUT \ http://localhost:8000/api/links/string123

{
  "original_url": "https://example12.com/"
}

Response:

	
Response body
Download
{
  "detail": "Ссылка обновлена"
}

**Инструкция по запуску (в т.ч. тестов):**

1) Установить все зависимости 
2) Docker docker-compose up -d 
3) Запустить python -m uvicorn app.main:app --reload 
4) Зайти http://localhost:8000/docs


**Описание БД**

Postgres
__tablename__ = "links"

    short_code = Column(String, primary_key=True, index=True)
    original_url = Column(String, nullable=False, unique=True)
    custom_alias = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    last_accessed = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=True)
