"""Параметризовані SQL-операції над категоріями та записами."""

import sqlite3
from contextlib import closing
from typing import Any

from labs.lab03.database import get_connection
from labs.lab03.schemas import CategoryCreate, RecordCreate, RecordReplace, Status


class ResourceNotFoundError(Exception):
    """Запитаний запис або категорію не знайдено."""


class ResourceConflictError(Exception):
    """Порушена унікальність або обмеження на видалення."""


_RECORD_SQL = """
SELECT r.id, r.code, r.title, r.category_id, r.value, r.status,
       c.name AS category_name
FROM records AS r
JOIN categories AS c ON c.id = r.category_id
"""


def _connect() -> sqlite3.Connection:
    """Відкрити нове з’єднання, яке повертає записи як словники."""
    connection = get_connection()
    connection.row_factory = sqlite3.Row
    return connection


def _as_dict(row: sqlite3.Row) -> dict[str, Any]:
    """Перетворити SQLite-рядок на звичайний словник."""
    return dict(row)


def _require_category(connection: sqlite3.Connection, category_id: int) -> None:
    """Переконатися, що категорія існує."""
    row = connection.execute(
        "SELECT id FROM categories WHERE id = ?", (category_id,)
    ).fetchone()
    if row is None:
        raise ResourceNotFoundError("Категорію не знайдено")


def _fetch_record(connection: sqlite3.Connection, record_id: int) -> dict[str, Any]:
    """Повернути запис із назвою категорії або помилку 404."""
    row = connection.execute(_RECORD_SQL + " WHERE r.id = ?", (record_id,)).fetchone()
    if row is None:
        raise ResourceNotFoundError("Запис не знайдено")
    return _as_dict(row)


def _handle_record_integrity(error: sqlite3.IntegrityError) -> None:
    """Відобразити очікувані обмеження БД у доменні помилки."""
    message = str(error).lower()
    if "foreign key" in message:
        raise ResourceNotFoundError("Категорію не знайдено") from error
    if "unique" in message:
        raise ResourceConflictError("Запис із таким кодом уже існує") from error
    raise error


def list_categories() -> list[dict[str, Any]]:
    """Отримати категорії у порядку зростання id."""
    with closing(_connect()) as connection:
        rows = connection.execute(
            "SELECT id, name FROM categories ORDER BY id ASC"
        ).fetchall()
        return [_as_dict(row) for row in rows]


def create_category(data: CategoryCreate) -> dict[str, Any]:
    """Створити категорію або повідомити про дублікат."""
    with closing(_connect()) as connection, connection:
        try:
            cursor = connection.execute(
                "INSERT INTO categories (name) VALUES (?)", (data.name,)
            )
        except sqlite3.IntegrityError as error:
            if "unique" in str(error).lower():
                raise ResourceConflictError(
                    "Категорія з такою назвою вже існує"
                ) from error
            raise
        row = connection.execute(
            "SELECT id, name FROM categories WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        return _as_dict(row)


def delete_category(category_id: int) -> None:
    """Видалити лише порожню категорію."""
    with closing(_connect()) as connection, connection:
        _require_category(connection, category_id)
        occupied = connection.execute(
            "SELECT 1 FROM records WHERE category_id = ? LIMIT 1",
            (category_id,),
        ).fetchone()
        if occupied:
            raise ResourceConflictError(
                "Категорію з наявними записами видаляти не можна"
            )
        try:
            connection.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        except sqlite3.IntegrityError as error:
            raise ResourceConflictError(
                "Категорію з наявними записами видаляти не можна"
            ) from error


def create_record(data: RecordCreate) -> dict[str, Any]:
    """Створити один запис; всі SQL-значення параметризовані."""
    with closing(_connect()) as connection, connection:
        _require_category(connection, data.category_id)
        try:
            cursor = connection.execute(
                """
                    INSERT INTO records
                        (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                (
                    data.code,
                    data.title,
                    data.category_id,
                    data.value,
                    data.status,
                ),
            )
        except sqlite3.IntegrityError as error:
            _handle_record_integrity(error)
        return _fetch_record(connection, cursor.lastrowid)


def get_record(record_id: int) -> dict[str, Any]:
    """Отримати один запис за id із JOIN категорії."""
    with closing(_connect()) as connection:
        return _fetch_record(connection, record_id)


def list_records(
    *,
    category_id: int | None = None,
    status: Status | None = None,
    min_value: int | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Виконати фільтри через AND, сортування та пагінацію."""
    sql_parts = [_RECORD_SQL, " WHERE 1 = 1"]
    parameters: list[Any] = []

    if category_id is not None:
        sql_parts.append(" AND r.category_id = ?")
        parameters.append(category_id)
    if status is not None:
        sql_parts.append(" AND r.status = ?")
        parameters.append(status)
    if min_value is not None:
        sql_parts.append(" AND r.value >= ?")
        parameters.append(min_value)
    if q is not None:
        sql_parts.append(" AND instr(r.title, ?) > 0")
        parameters.append(q)

    sql_parts.append(" ORDER BY r.id ASC LIMIT ? OFFSET ?")
    parameters.extend((limit, offset))

    with closing(_connect()) as connection:
        rows = connection.execute("".join(sql_parts), parameters).fetchall()
        return [_as_dict(row) for row in rows]


def replace_record(record_id: int, data: RecordReplace) -> dict[str, Any]:
    """Повністю змінити поля запису, залишивши id незмінним."""
    with closing(_connect()) as connection, connection:
        _fetch_record(connection, record_id)
        _require_category(connection, data.category_id)
        try:
            connection.execute(
                """
                    UPDATE records
                    SET code = ?, title = ?, category_id = ?,
                        value = ?, status = ?
                    WHERE id = ?
                    """,
                (
                    data.code,
                    data.title,
                    data.category_id,
                    data.value,
                    data.status,
                    record_id,
                ),
            )
        except sqlite3.IntegrityError as error:
            _handle_record_integrity(error)
        return _fetch_record(connection, record_id)


def delete_record(record_id: int) -> None:
    """Видалити запис і повернути 404 для відсутнього id."""
    with closing(_connect()) as connection, connection:
        cursor = connection.execute("DELETE FROM records WHERE id = ?", (record_id,))
        if cursor.rowcount == 0:
            raise ResourceNotFoundError("Запис не знайдено")


def bulk_create_records(items: list[RecordCreate]) -> list[dict[str, Any]]:
    """Атомарно додати пакет; будь-яка помилка скасовує всі INSERT."""
    with closing(_connect()) as connection, connection:
        result: list[dict[str, Any]] = []
        for data in items:
            _require_category(connection, data.category_id)
            try:
                cursor = connection.execute(
                    """
                        INSERT INTO records
                            (code, title, category_id, value, status)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                    (
                        data.code,
                        data.title,
                        data.category_id,
                        data.value,
                        data.status,
                    ),
                )
            except sqlite3.IntegrityError as error:
                _handle_record_integrity(error)
            result.append(_fetch_record(connection, cursor.lastrowid))
        return result
