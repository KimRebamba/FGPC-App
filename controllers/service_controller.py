"""Service and category application operations."""

from __future__ import annotations

import sqlite3

from models.category import Category
from models.service import Service
from models.service_image import ServiceImage


def list_categories(
    active_only: bool = False,
    include_deleted: bool = False,
    database_path: str | None = None,
) -> list[Category]:
    return Category.list_all(active_only, include_deleted, database_path)


def create_category(
    category_name: str,
    description: str | None = None,
    image_path: str | None = None,
    database_path: str | None = None,
) -> Category:
    if not category_name.strip():
        raise ValueError("Category name is required.")
    try:
        return Category.create(
            category_name.strip(), description, image_path, database_path
        )
    except sqlite3.IntegrityError as error:
        if "UNIQUE constraint failed: Categories.category_name" in str(error):
            raise ValueError("A category with this name already exists.") from error
        raise


def update_category(
    category_id: int,
    category_name: str,
    description: str | None = None,
    image_path: str | None = None,
    database_path: str | None = None,
) -> Category:
    if not category_name.strip():
        raise ValueError("Category name is required.")
    try:
        updated = Category.update(
            category_id=category_id,
            category_name=category_name.strip(),
            description=description,
            image_path=image_path,
            database_path=database_path,
        )
    except sqlite3.IntegrityError as error:
        if "UNIQUE constraint failed: Categories.category_name" in str(error):
            raise ValueError("A category with this name already exists.") from error
        raise
    if updated is None:
        raise ValueError("Category not found.")
    return updated


def delete_category(category_id: int, database_path: str | None = None) -> bool:
    success = Category.delete(category_id, database_path)
    if not success:
        raise ValueError("Category not found or cannot be deleted.")
    return True


def delete_categories(category_ids: list[int], database_path: str | None = None) -> int:
    return Category.delete_many(category_ids, database_path)


def list_services(
    category_id: int | None = None,
    available_only: bool = False,
    include_deleted: bool = False,
    database_path: str | None = None,
) -> list[Service]:
    return Service.list_all(category_id, available_only, include_deleted, database_path)


def create_service(
    category_id: int,
    service_name: str,
    price: float,
    duration_minutes: int,
    description: str | None = None,
    image_path: str | None = None,
    database_path: str | None = None,
) -> Service:
    if not service_name.strip():
        raise ValueError("Service name is required.")
    if price < 0:
        raise ValueError("Price cannot be negative.")
    if duration_minutes <= 0:
        raise ValueError("Duration must be greater than zero.")
    category = Category.find_by_id(category_id, database_path)
    if category is None or category.is_deleted:
        raise ValueError("Category not found.")
    return Service.create(
        category_id,
        service_name.strip(),
        price,
        duration_minutes,
        description,
        image_path,
        database_path,
    )


def update_service(
    service_id: int,
    category_id: int,
    service_name: str,
    price: float,
    duration_minutes: int,
    description: str | None = None,
    image_path: str | None = None,
    database_path: str | None = None,
) -> Service:
    if not service_name.strip():
        raise ValueError("Service name is required.")
    if price < 0:
        raise ValueError("Price cannot be negative.")
    if duration_minutes <= 0:
        raise ValueError("Duration must be greater than zero.")
    category = Category.find_by_id(category_id, database_path)
    if category is None or category.is_deleted:
        raise ValueError("Category not found.")
    updated = Service.update(
        service_id=service_id,
        category_id=category_id,
        service_name=service_name.strip(),
        price=price,
        duration_minutes=duration_minutes,
        description=description,
        image_path=image_path,
        database_path=database_path,
    )
    if updated is None:
        raise ValueError("Service not found.")
    return updated


def delete_service(service_id: int, database_path: str | None = None) -> bool:
    success = Service.delete(service_id, database_path)
    if not success:
        raise ValueError("Service not found or cannot be deleted.")
    return True


def delete_services(service_ids: list[int], database_path: str | None = None) -> int:
    return Service.delete_many(service_ids, database_path)


def add_service_image(
    service_id: int,
    image_path: str,
    is_primary: bool = False,
    database_path: str | None = None,
) -> ServiceImage:
    if not image_path.strip():
        raise ValueError("Image path is required.")
    if Service.find_by_id(service_id, database_path) is None:
        raise ValueError("Service not found.")
    return ServiceImage.create(
        service_id, image_path.strip(), is_primary, database_path
    )


def list_service_images(
    service_id: int, database_path: str | None = None
) -> list[ServiceImage]:
    return ServiceImage.list_for_service(service_id, database_path)


def set_category_active(
    category_id: int, is_active: bool, database_path: str | None = None
) -> Category:
    category = Category.set_active(category_id, is_active, database_path)
    if category is None:
        raise ValueError("Category not found.")
    return category


def set_service_available(
    service_id: int, is_available: bool, database_path: str | None = None
) -> Service:
    service = Service.set_available(service_id, is_available, database_path)
    if service is None:
        raise ValueError("Service not found.")
    return service