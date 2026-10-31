"""Authentication and user-account application operations."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3

from models.user import User

HASH_ALGORITHM = "pbkdf2_sha256"
HASH_ITERATIONS = 310_000


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, HASH_ITERATIONS
    )
    return f"{HASH_ALGORITHM}${HASH_ITERATIONS}${salt.hex()}${digest.hex()}"


def _verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded_hash.split("$")
        if algorithm != HASH_ALGORITHM:
            return False
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(actual, expected)


def register_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    address: str | None = None,
    contact_number: str | None = None,
    role: str = "customer",
    database_path: str | None = None,
) -> User:
    if not first_name.strip() or not last_name.strip():
        raise ValueError("First name and last name are required.")
    if not email.strip() or "@" not in email:
        raise ValueError("A valid email address is required.")
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")
    if role not in {"customer", "admin"}:
        raise ValueError("Invalid user role.")
    try:
        return User.create(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email.strip().lower(),
            password_hash=_hash_password(password),
            address=address.strip() if address else None,
            contact_number=contact_number.strip() if contact_number else None,
            role=role,
            database_path=database_path,
        )
    except sqlite3.IntegrityError as error:
        if "UNIQUE constraint failed: Users.email" in str(error):
            raise ValueError("An account with this email already exists.") from error
        raise


def authenticate_user(
    email: str, password: str, database_path: str | None = None
) -> User | None:
    user = User.find_by_email(email.strip().lower(), database_path)
    if user is None or not user.is_active:
        return None
    return user if _verify_password(password, user.password_hash) else None


def update_user_profile(
    user_id: int,
    first_name: str,
    last_name: str,
    address: str | None,
    contact_number: str | None,
    profile_image: str | None = None,
    database_path: str | None = None,
) -> User:
    if not first_name.strip() or not last_name.strip():
        raise ValueError("First name and last name are required.")
    user = User.find_by_id(user_id, database_path)
    if user is None:
        raise ValueError("User not found.")
    return user.update_profile(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        address=address.strip() if address else None,
        contact_number=contact_number.strip() if contact_number else None,
        profile_image=profile_image,
        database_path=database_path,
    )


def admin_create_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    role: str = "customer",
    address: str | None = None,
    contact_number: str | None = None,
    profile_image: str | None = None,
    database_path: str | None = None,
) -> User:
    if not first_name.strip() or not last_name.strip():
        raise ValueError("First name and last name are required.")
    if not email.strip() or "@" not in email:
        raise ValueError("A valid email address is required.")
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")
    if role not in {"customer", "admin"}:
        raise ValueError("Invalid user role.")
    try:
        return User.create(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email.strip().lower(),
            password_hash=_hash_password(password),
            address=address.strip() if address else None,
            contact_number=contact_number.strip() if contact_number else None,
            role=role,
            profile_image=profile_image,
            database_path=database_path,
        )
    except sqlite3.IntegrityError as error:
        if "UNIQUE constraint failed: Users.email" in str(error):
            raise ValueError("An account with this email already exists.") from error
        raise


def admin_update_user(
    user_id: int,
    first_name: str,
    last_name: str,
    email: str,
    role: str,
    is_active: bool,
    address: str | None = None,
    contact_number: str | None = None,
    profile_image: str | None = None,
    database_path: str | None = None,
) -> User:
    if not first_name.strip() or not last_name.strip():
        raise ValueError("First name and last name are required.")
    if not email.strip() or "@" not in email:
        raise ValueError("A valid email address is required.")
    if role not in {"customer", "admin"}:
        raise ValueError("Invalid user role.")
    updated = User.admin_update(
        user_id=user_id,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        email=email.strip().lower(),
        role=role,
        is_active=is_active,
        address=address.strip() if address else None,
        contact_number=contact_number.strip() if contact_number else None,
        profile_image=profile_image,
        database_path=database_path,
    )
    if updated is None:
        raise ValueError("User not found.")
    return updated


def set_user_active(
    user_id: int, is_active: bool, database_path: str | None = None
) -> User:
    user = User.set_active(user_id, is_active, database_path)
    if user is None:
        raise ValueError("User not found.")
    return user


def delete_user(user_id: int, database_path: str | None = None) -> bool:
    success = User.delete(user_id, database_path)
    if not success:
        raise ValueError("User not found or cannot be deleted.")
    return True


def delete_users(user_ids: list[int], database_path: str | None = None) -> int:
    return User.delete_many(user_ids, database_path)


def verify_user_password(
    user_id: int, current_password: str, database_path: str | None = None
) -> bool:
    user = User.find_by_id(user_id, database_path)
    if user is None:
        return False
    return _verify_password(current_password, user.password_hash)


def change_user_password(
    user_id: int,
    current_password: str,
    new_password: str,
    database_path: str | None = None,
) -> bool:
    if not current_password:
        raise ValueError("Current password is required.")
    if not verify_user_password(user_id, current_password, database_path):
        raise ValueError("Current password is incorrect.")
    if len(new_password) < 8:
        raise ValueError("New password must contain at least 8 characters.")
    if current_password == new_password:
        raise ValueError("New password cannot be the same as your current password.")
    new_hash = _hash_password(new_password)
    success = User.update_password(user_id, new_hash, database_path)
    if not success:
        raise ValueError("Failed to update password.")
    return True