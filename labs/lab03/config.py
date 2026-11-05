"""Налаштування варіанта 6 (події поштової безпеки)."""

VARIANT = 6
APP_TITLE = "Облік подій поштової безпеки"
APP_DESCRIPTION = (
    "Навчальний API для обліку перевірок поштових повідомлень. "
    "Категорії: phishing, malicious_attachment, spam. "
    "Поле value — невід'ємна ціла кількість подій (events); "
    "порогове значення — 10 events."
)
UNIT = "events"
THRESHOLD = 10
CATEGORY_NAMES = ("phishing", "malicious_attachment", "spam")
VALID_STATUSES = ("new", "in_progress", "done")
