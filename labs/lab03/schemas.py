"""Pydantic-моделі для перевірки запитів і відповідей."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["new", "in_progress", "done"]


class ValidatedModel(BaseModel):
    """Базова модель: обрізання пробілів і заборона невідомих полів."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class CategoryCreate(ValidatedModel):
    """Дані для створення категорії."""

    name: str = Field(min_length=2, max_length=40)


class CategoryRead(CategoryCreate):
    """Категорія разом із її ідентифікатором."""

    id: int = Field(strict=True, gt=0)


class RecordCreate(ValidatedModel):
    """Дані нового запису (без id, який створить SQLite)."""

    code: str = Field(min_length=3, max_length=40)
    title: str = Field(min_length=3, max_length=120)
    category_id: int = Field(strict=True, gt=0)
    value: int = Field(strict=True, ge=0)
    status: Status


class RecordReplace(RecordCreate):
    """Повна заміна всіх змінюваних полів запису."""


class RecordRead(RecordCreate):
    """Запис із id і назвою пов'язаної категорії."""

    id: int = Field(strict=True, gt=0)
    category_name: str


class StudentRead(BaseModel):
    """Дані студента, взяті з shared.student."""

    student_name: str
    group_name: str
    variant_number: int
