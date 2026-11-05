"""HTTP-маршрути для обліку подій поштової безпеки."""

from typing import Annotated

from fastapi import APIRouter, Body, Path, Query, status

from labs.lab03 import repository
from labs.lab03.schemas import RecordCreate, RecordRead, RecordReplace, Status

router = APIRouter(prefix="/records", tags=["Записи"])

NOT_FOUND = {404: {"description": "Запис або категорію не знайдено"}}
CONFLICT = {409: {"description": "Дублікат коду або інший конфлікт даних"}}


@router.get(
    "",
    response_model=list[RecordRead],
    summary="Список записів із фільтрами та пагінацією",
)
def get_records(
    category_id: Annotated[int | None, Query(gt=0)] = None,
    status_value: Annotated[Status | None, Query(alias="status")] = None,
    min_value: Annotated[int | None, Query(ge=0)] = None,
    q: Annotated[str | None, Query(min_length=1, max_length=120)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[dict]:
    """Поєднати фільтри через AND; пошук q буквальний і чутливий до регістру."""
    return repository.list_records(
        category_id=category_id,
        status=status_value,
        min_value=min_value,
        q=q,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/bulk",
    response_model=list[RecordRead],
    status_code=status.HTTP_201_CREATED,
    responses={**NOT_FOUND, **CONFLICT},
    summary="Атомарно додати 1–100 записів",
)
def post_bulk(
    records: Annotated[list[RecordCreate], Body(min_length=1, max_length=100)],
) -> list[dict]:
    """Зберегти всі записи однією транзакцією або скасувати пакет."""
    return repository.bulk_create_records(records)


@router.get(
    "/{record_id}",
    response_model=RecordRead,
    responses=NOT_FOUND,
    summary="Отримати запис за id",
)
def get_record(record_id: Annotated[int, Path(gt=0)]) -> dict:
    """Повернути запис та назву категорії."""
    return repository.get_record(record_id)


@router.post(
    "",
    response_model=RecordRead,
    status_code=status.HTTP_201_CREATED,
    responses={**NOT_FOUND, **CONFLICT},
    summary="Створити запис",
)
def post_record(data: RecordCreate) -> dict:
    """Додати новий навчальний запис."""
    return repository.create_record(data)


@router.put(
    "/{record_id}",
    response_model=RecordRead,
    responses={**NOT_FOUND, **CONFLICT},
    summary="Повністю замінити дані запису",
)
def put_record(
    record_id: Annotated[int, Path(gt=0)],
    data: RecordReplace,
) -> dict:
    """Замінити всі змінювані поля, зберігши id."""
    return repository.replace_record(record_id, data)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=NOT_FOUND,
    summary="Видалити запис",
)
def remove_record(record_id: Annotated[int, Path(gt=0)]) -> None:
    """Видалити запис з бази."""
    repository.delete_record(record_id)
