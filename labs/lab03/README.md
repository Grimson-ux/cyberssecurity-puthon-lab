# Лабораторна робота №3 — FastAPI + SQLite, варіант 6

**Тема:** прикладні бібліотеки Python для побудови вебзастосунків.

Предметна область: облік результатів навчальної перевірки поштових
повідомлень. Категорії: `phishing`, `malicious_attachment`, `spam`.
Поле `value` — ціла кількість подій (одиниця `events`, від 0 без верхньої
межі); навчальний поріг — **10 подій**.
`status`: `new`, `in_progress`, `done`.

## Установлення

Команди виконуйте з **кореня** репозиторію `cybersecurity-python-labs`.
Потрібен Python 3.10+ і наявний файл `shared/student.py`.

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

У наявному `requirements.txt` мають бути `fastapi`, `uvicorn`,
`pydantic` (версія 2) та `ruff`. Попередні залежності не видаляйте.

Якщо `.venv` ще немає:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Створення бази та запуск

```powershell
python -m labs.lab03.database
python -m labs.lab03.seed
python -m labs.lab03.seed
uvicorn labs.lab03.main:app --reload --host 127.0.0.1 --port 8000
```

Другий запуск seed повідомляє, що база не порожня, і не змінює даних.

Документація та API:

- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json
- Перевірка: http://127.0.0.1:8000/ping
- Дані студента: http://127.0.0.1:8000/student

Якщо в `shared/student.py` інше ім'я змінної ПІБ, використовуйте
`STUDENT_NAME`, `FULL_NAME`, `STUDENT_FULL_NAME`, `NAME` або пару
`LAST_NAME` + `FIRST_NAME`. `GROUP_NAME` і `VARIANT_NUMBER`
беруться безпосередньо з `shared.student`.

## Структура

```text
labs/lab03/
├── __init__.py
├── config.py
├── database.py
├── schema.sql
├── repository.py
├── schemas.py
├── seed.py
├── main.py
├── routers/
│   ├── __init__.py
│   ├── categories.py
│   └── records.py
├── data/
│   └── seed.json
└── README.md
```

Файл `data/lab3.sqlite3` генерується автоматично і **не додається в Git**.

## Основні запити (Swagger UI)

| Метод | Маршрут | Дія |
|---|---|---|
| GET | `/ping` | Повернути `{"status":"ok"}` |
| GET | `/student` | ПІБ, група, варіант |
| GET | `/categories` | Категорії за id |
| POST | `/categories` | Створення категорії |
| DELETE | `/categories/{category_id}` | Видалення порожньої категорії |
| GET | `/records` | Записи, фільтри та пагінація |
| GET | `/records/{record_id}` | Запис за id |
| POST | `/records` | Створення запису |
| PUT | `/records/{record_id}` | Заміна усіх п'яти полів |
| DELETE | `/records/{record_id}` | Видалення |
| POST | `/records/bulk` | Атомарне додавання 1–100 записів |

Приклад для `POST /records`:

```json
{
  "code": "V06-TEST",
  "title": "Тестове спостереження",
  "category_id": 1,
  "value": 14,
  "status": "new"
}
```

Приклад для фільтрації:

```text
GET /records?category_id=1&status=new&min_value=10&limit=5&offset=0
```

Параметр `q` шукає **буквальний** підрядок у `title` з урахуванням
регістру. SQL-ін'єкції не спрацюють, бо значення передаються лише через `?`.

Приклад для `POST /records/bulk`:

```json
[
  {
    "code": "V06-BULK01",
    "title": "Нове спостереження 01",
    "category_id": 1,
    "value": 20,
    "status": "new"
  },
  {
    "code": "V06-BULK02",
    "title": "Нове спостереження 02",
    "category_id": 2,
    "value": 7,
    "status": "done"
  }
]
```

Якщо код уже є, відповідь буде **409**. Якщо категорії немає —
**404**. Обидва записи не збережуться, якщо будь-який елемент помилковий.
Некоректні дані дають **422**.

## Перевірка Ruff

```powershell
ruff check labs/lab03
ruff format --check labs/lab03
ruff check .
ruff format --check .
```

За потреби:

```powershell
ruff check --fix labs/lab03
ruff format labs/lab03
```

## GitHub

Перевірте `.gitignore` і виконайте:

```powershell
git status
git add labs/lab03 requirements.txt .gitignore
git commit -m "Add lab 3 FastAPI and SQLite application"
git push
```

Якщо створили `labs/__init__.py`, додайте його окремо.

**Примітка:** HTTP-коди та транзакції перевіряйте самостійно через
Swagger UI; Ruff перевіряє стиль, а не поведінку API.
