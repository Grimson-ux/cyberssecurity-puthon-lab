"""HTTP-маршрути для категорій."""

from typing import Annotated

from fastapi import APIRouter, Path, status

from labs.lab03 import repository
from labs.lab03.schemas import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["Категорії"])

NOT_FOUND = {404: {"description": "Категорії не знайдено"}}
CONFLICT = {409: {"description": "Дублікат або категорія містить записи"}}


@router.get(
    "",
    response_model=list[CategoryRead],
    summary="Список категорій",
)
def get_categories() -> list[dict]:
    """Показати категорії за зростанням id."""
    return repository.list_categories()


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    responses=CONFLICT,
    summary="Створити категорію",
)
def post_category(data: CategoryCreate) -> dict:
    """Створити категорію, якщо її назва унікальна."""
    return repository.create_category(data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**NOT_FOUND, **CONFLICT},
    summary="Видалити порожню категорію",
)
def remove_category(category_id: Annotated[int, Path(gt=0)]) -> None:
    """Заборонити видалення, якщо категорія використовується."""
    repository.delete_category(category_id)
