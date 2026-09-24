import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

MIN_PASSWORD_LENGTH = 9
SALT = str(VARIANT_NUMBER).zfill(5)

DATA_DIR = Path("labs/lab01/data")
USERS_FILE = DATA_DIR / "users.csv"
LOG_FILE = DATA_DIR / "log.json"


class ValidationError(Exception):
    pass


def generate_hash(password: str, salt: str = "00000") -> str:
    if not password or not salt:
        raise ValueError("Password and salt cannot be empty")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(
            f"Password must contain at least {MIN_PASSWORD_LENGTH} characters"
        )

    text = password + salt

    return hashlib.blake2s(text.encode()).hexdigest()


def create_user(username, password):
    password_hash = generate_hash(password, SALT)

    return username, password_hash


def create_users(users_list):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with USERS_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        for username, password in users_list:
            user = create_user(username, password)
            writer.writerow(user)


def load_users():
    users_db = {}

    with USERS_FILE.open("r", encoding="utf-8") as file:
        reader = csv.reader(file)

        for username, password_hash in reader:
            users_db[username] = password_hash

    return users_db


def log_event(function):
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)

        event = {
            "event": "login",
            "user": args[0] if args else "unknown",
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "args": list(args),
            "kwargs": kwargs,
        }

        logs = []

        if LOG_FILE.exists():
            try:
                with LOG_FILE.open("r", encoding="utf-8") as file:
                    logs = json.load(file)
            except json.JSONDecodeError:
                logs = []

        logs.append(event)

        with LOG_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                logs,
                file,
                ensure_ascii=False,
                indent=4,
            )

        return result

    return wrapper


@log_event
def login(username, password):
    if not username or not password:
        raise ValueError("Username and password cannot be empty")

    users_db = load_users()

    if username not in users_db:
        return False

    entered_hash = generate_hash(password, SALT)

    return users_db[username] == entered_hash


def main():
    print(STUDENT_NAME)
    print(GROUP_NAME)
    print(VARIANT_NUMBER)
    print("Algorithm: blake2s")
    print("Salt:", SALT)

    users_to_register = (
        ("red_team_lead", "RedTeam#2026"),
        ("blue_team_analyst", "BlueTeam#2026"),
        ("purple_team_coord", "Purple#2026"),
        ("student_intern", "Student#2026"),
        ("security_admin", "Security#2026"),
        ("network_admin", "Network#2026"),
        ("forensic_expert", "Forensic#2026"),
        ("malware_analyst", "Malware#2026"),
        ("soc_analyst", "SocTeam#2026"),
        ("pentest_user", "Pentest#2026"),
    )

    try:
        create_users(users_to_register)

        users_db = load_users()

        print("\nUsers database:")

        for username, password_hash in users_db.items():
            print(username, "->", password_hash)

        print("\nLogin tests:")

        print(
            "red_team_lead:",
            login("red_team_lead", "RedTeam#2026"),
        )

        print(
            "student_intern:",
            login("student_intern", "WrongPassword"),
        )

        print(
            "unknown_user:",
            login("unknown_user", "Password123"),
        )

    except FileNotFoundError as error:
        print("File not found:", error)

    except PermissionError as error:
        print("Permission error:", error)

    except OSError as error:
        print("Input/output error:", error)

    except ValidationError as error:
        print("Validation error:", error)

    except ValueError as error:
        print("Value error:", error)


if __name__ == "__main__":
    main()