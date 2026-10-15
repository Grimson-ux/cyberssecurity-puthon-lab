import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


PBKDF2_ITERATIONS = 100_000
SESSION_TIMEOUT_SEC = 900


class User:
    EMAIL_PATTERN = re.compile(
        r"^[A-Za-z][A-Za-z0-9_]{2,63}"
        r"@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
    )

    # Створення нового користувача
    def __init__(
        self,
        username: str,
        email: str,
        role: str = "user",
        active: bool = True,
    ):
        self.username = username
        self.email = email
        self.role = role
        self.active = active

        self.__password_hash: bytes | None = None
        self.__password_salt: bytes | None = None

    # Отримання email користувача
    @property
    def email(self) -> str:
        return self._email

    # Встановлення email з перевіркою формату
    @email.setter
    def email(self, value: str) -> None:
        if not self.EMAIL_PATTERN.fullmatch(value):
            raise ValueError("Invalid email format")

        self._email = value

    # Хешування та збереження пароля
    def set_password(self, password: str) -> None:
        self.__password_salt = os.urandom(16)

        self.__password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            self.__password_salt,
            PBKDF2_ITERATIONS,
        )

    # Перевірка правильності введеного пароля
    def check_password(self, password: str) -> bool:
        if self.__password_hash is None or self.__password_salt is None:
            return False

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            self.__password_salt,
            PBKDF2_ITERATIONS,
        )

        return hmac.compare_digest(
            password_hash,
            self.__password_hash,
        )

    # Деактивація користувача
    def deactivate(self) -> None:
        self.active = False

    # Текстове представлення користувача
    def __str__(self) -> str:
        return (
            f"User(username={self.username}, "
            f"email={self.email}, "
            f"role={self.role}, "
            f"active={self.active})"
        )


class Admin(User):

    # Створення адміністратора з набором прав
    def __init__(
        self,
        username: str,
        email: str,
        permissions: set[str] | None = None,
    ):
        super().__init__(
            username=username,
            email=email,
            role="admin",
        )

        if permissions is None:
            permissions = set()

        self.permissions = permissions

    # Додавання нового права
    def grant_permission(self, permission: str) -> None:
        self.permissions.add(permission)

    # Видалення права
    def revoke_permission(self, permission: str) -> None:
        self.permissions.discard(permission)

    # Перевірка наявності права
    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    # Текстове представлення адміністратора
    def __str__(self) -> str:
        return (
            f"Admin(username={self.username}, "
            f"email={self.email}, "
            f"permissions={sorted(self.permissions)}, "
            f"active={self.active})"
        )


class Session:

    # Створення нової сесії користувача
    def __init__(self, ip: str):
        self.ip = ip
        self.login_time = datetime.now(timezone.utc)
        self.last_activity = self.login_time

    # Оновлення часу останньої активності
    def touch(self) -> None:
        self.last_activity = datetime.now(timezone.utc)

    # Перевірка, чи сесія ще активна
    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec <= 0:
            raise ValueError("timeout_sec must be greater than 0")

        current_time = datetime.now(timezone.utc)
        inactive_time = current_time - self.last_activity

        return inactive_time < timedelta(seconds=timeout_sec)


@dataclass
class AuditRecord:
    timestamp: datetime
    username: str
    action: str


class AuditLog:

    # Створення порожнього журналу подій
    def __init__(self):
        self.records: list[AuditRecord] = []

    # Додавання нового запису до журналу
    def add_log(self, username: str, action: str) -> None:
        record = AuditRecord(
            timestamp=datetime.now(timezone.utc),
            username=username,
            action=action,
        )

        self.records.append(record)

    # Виведення всіх записів журналу
    def show_all(self) -> None:
        for record in self.records:
            print(
                f"{record.timestamp} | "
                f"{record.username} | "
                f"{record.action}"
            )


class UserAccount:

    # Створення облікового запису користувача
    def __init__(
        self,
        user: User,
        session: Session | None = None,
        audit_log: AuditLog | None = None,
    ):
        self.user = user
        self.session = session

        if audit_log is None:
            audit_log = AuditLog()

        self.audit_log = audit_log

    # Авторизація користувача
    def login(
        self,
        username: str,
        password: str,
        ip: str,
    ) -> bool:
        if not self.user.active:
            self.audit_log.add_log(
                self.user.username,
                "login_failure",
            )
            return False

        if username != self.user.username:
            self.audit_log.add_log(
                username,
                "login_failure",
            )
            return False

        if not self.user.check_password(password):
            self.audit_log.add_log(
                username,
                "login_failure",
            )
            return False

        self.session = Session(ip)
        self.session.touch()

        self.audit_log.add_log(
            username,
            "login_success",
        )

        return True

    # Перевірка стану авторизації
    def is_authenticated(self) -> bool:
        if self.session is None:
            return False

        if not self.session.is_active(SESSION_TIMEOUT_SEC):
            self.session = None
            return False

        return True

    # Завершення поточної сесії
    def logout(self) -> None:
        if self.session is not None:
            self.audit_log.add_log(
                self.user.username,
                "logout",
            )

        self.session = None

    # Отримання дозволених атрибутів через ключ
    def __getitem__(self, key: str):
        if key == "user":
            return self.user

        if key == "session":
            return self.session

        if key == "audit_log":
            return self.audit_log

        raise KeyError(key)

    # Зміна дозволених атрибутів через ключ
    def __setitem__(self, key: str, value) -> None:
        if key == "user":
            if not isinstance(value, User):
                raise TypeError("user must be an instance of User")

            self.user = value
            return

        if key == "session":
            if value is not None and not isinstance(value, Session):
                raise TypeError(
                    "session must be an instance of Session or None"
                )

            self.session = value
            return

        if key == "audit_log":
            if not isinstance(value, AuditLog):
                raise TypeError(
                    "audit_log must be an instance of AuditLog"
                )

            self.audit_log = value
            return

        raise KeyError(key)