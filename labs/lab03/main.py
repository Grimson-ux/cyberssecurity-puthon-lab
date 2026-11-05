"""Точка входу FastAPI-застосунку лабораторної №3."""

import logging
import sqlite3
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from labs.lab03 import repository
from labs.lab03.config import APP_DESCRIPTION, APP_TITLE
from labs.lab03.database import initialize_database
from labs.lab03.routers import categories, records
from labs.lab03.schemas import StudentRead
from shared import student

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Створити відсутні таблиці один раз під час запуску API."""
    initialize_database()
    yield


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(categories.router)
app.include_router(records.router)


@app.exception_handler(repository.ResourceNotFoundError)
def handle_not_found(
    _request: Request, exc: repository.ResourceNotFoundError
) -> JSONResponse:
    """Перетворити відсутній ресурс на HTTP 404."""
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(repository.ResourceConflictError)
def handle_conflict(
    _request: Request, exc: repository.ResourceConflictError
) -> JSONResponse:
    """Перетворити конфлікт даних на HTTP 409."""
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(sqlite3.Error)
def handle_sqlite_error(_request: Request, exc: sqlite3.Error) -> JSONResponse:
    """Не розкривати деталі SQL або шляхів до файлів клієнту."""
    logger.error("SQLite operation failed", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутрішня помилка роботи з базою даних"},
    )


@app.get("/ping", tags=["Сервіс"], summary="Перевірити доступність API")
def ping() -> dict[str, str]:
    """Відповісти на перевірку працездатності."""
    return {"status": "ok"}


@app.get(
    "/student",
    response_model=StudentRead,
    tags=["Сервіс"],
    summary="Отримати дані студента",
)
def get_student() -> dict[str, Any]:
    """Взяти ПІБ, групу та варіант з наявного shared/student.py."""
    name = next(
        (
            value
            for attribute in ("STUDENT_NAME", "FULL_NAME", "STUDENT_FULL_NAME", "NAME")
            if isinstance(value := getattr(student, attribute, None), str) and value
        ),
        None,
    )
    if name is None:
        first_name = getattr(student, "FIRST_NAME", "")
        last_name = getattr(student, "LAST_NAME", "")
        name = f"{last_name} {first_name}".strip()

    return {
        "student_name": name,
        "group_name": student.GROUP_NAME,
        "variant_number": student.VARIANT_NUMBER,
    }
