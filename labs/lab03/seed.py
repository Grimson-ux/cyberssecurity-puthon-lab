"""Завантажити три категорії та вісім записів однією транзакцією."""

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from labs.lab03.config import CATEGORY_NAMES, VARIANT
from labs.lab03.database import get_connection, initialize_database
from labs.lab03.schemas import CategoryRead, RecordCreate

SEED_PATH = Path(__file__).resolve().parent / "data" / "seed.json"


class SeedPayload(BaseModel):
    """Початковий JSON визначеної структури."""

    model_config = ConfigDict(extra="forbid")
    categories: list[CategoryRead] = Field(min_length=3, max_length=3)
    records: list[RecordCreate] = Field(min_length=8, max_length=8)


def _validate_seed(data: SeedPayload) -> None:
    """Перевірити ідентифікатори, назви та посилання в JSON."""
    expected_categories = list(enumerate(CATEGORY_NAMES, start=1))
    actual_categories = [(item.id, item.name) for item in data.categories]
    if actual_categories != expected_categories:
        raise ValueError("Потрібні категорії варіанта 6 з id 1, 2, 3")

    codes = [record.code for record in data.records]
    if len(set(codes)) != len(codes):
        raise ValueError("У початковому JSON дублюються code")
    category_ids = {item.id for item in data.categories}
    for index, record in enumerate(data.records, start=1):
        if record.category_id not in category_ids:
            raise ValueError(f"Запис {index}: невідома категорія")
        if record.code != f"V{VARIANT:02d}-{index:02d}":
            raise ValueError(f"Запис {index}: неправильний формат code")


def seed_database() -> bool:
    """Заповнити тільки порожню базу; false означає пропуск без змін."""
    raw = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    data = SeedPayload.model_validate(raw)
    _validate_seed(data)
    initialize_database()

    with closing(get_connection()) as connection, connection:
        old_categories = connection.execute(
            "SELECT EXISTS(SELECT 1 FROM categories)"
        ).fetchone()[0]
        old_records = connection.execute(
            "SELECT EXISTS(SELECT 1 FROM records)"
        ).fetchone()[0]
        if old_categories or old_records:
            return False

        connection.executemany(
            "INSERT INTO categories (id, name) VALUES (?, ?)",
            [(item.id, item.name) for item in data.categories],
        )
        connection.executemany(
            """
                INSERT INTO records (code, title, category_id, value, status)
                VALUES (?, ?, ?, ?, ?)
                """,
            [
                (
                    item.code,
                    item.title,
                    item.category_id,
                    item.value,
                    item.status,
                )
                for item in data.records
            ],
        )
    return True


def main() -> None:
    """Запустити seed із зрозумілим повідомленням."""
    try:
        created = seed_database()
    except (OSError, ValueError, ValidationError, sqlite3.Error) as error:
        print(f"Помилка початкового заповнення: {error}")
        raise SystemExit(1) from None
    if created:
        print("Готово: додано 3 категорії та 8 записів.")
    else:
        print("База не порожня: повторне заповнення пропущено, дані незмінні.")


if __name__ == "__main__":
    main()
