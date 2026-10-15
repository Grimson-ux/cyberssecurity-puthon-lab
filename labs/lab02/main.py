import argparse
import logging
from datetime import timedelta

from labs.lab02.task1 import Admin, UserAccount
from labs.lab02.task2 import (
    DEFAULT_OUTPUT,
    DEFAULT_WORDLIST,
    run_analysis,
)


# Демонстрація роботи класів із Завдання 1
def run_demo() -> None:
    print("=== LAB 02 - TASK 1 DEMO ===")

    admin = Admin(
        username="Vadym",
        email="vadym123@gmail.com",
    )

    admin.set_password("Qwerty123!")

    print("\n--- USER CREATED ---")
    print(admin)

    print("\n--- ADMIN PERMISSIONS ---")

    admin.grant_permission("read_logs")
    admin.grant_permission("delete_users")

    print(
        "read_logs:",
        admin.has_permission("read_logs"),
    )

    print(
        "delete_users:",
        admin.has_permission("delete_users"),
    )

    admin.revoke_permission("delete_users")

    print(
        "delete_users after revoke:",
        admin.has_permission("delete_users"),
    )

    account = UserAccount(admin)

    print("\n--- FAILED LOGIN ---")

    result = account.login(
        username="Vadym",
        password="WrongPassword",
        ip="192.168.1.10",
    )

    print("Login result:", result)

    print("\n--- SUCCESSFUL LOGIN ---")

    result = account.login(
        username="Vadym",
        password="Qwerty123!",
        ip="192.168.1.10",
    )

    print("Login result:", result)
    print(
        "Authenticated:",
        account.is_authenticated(),
    )

    if account.session is not None:
        print(
            "Session IP:",
            account.session.ip,
        )
        print(
            "Login time:",
            account.session.login_time,
        )

    print("\n--- EMAIL VALIDATION ---")

    try:
        admin.email = "123bad@email.com"

    except ValueError as error:
        print(
            "Invalid email:",
            error,
        )

    admin.email = "vadym_new@gmail.com"

    print(
        "Valid new email:",
        admin.email,
    )

    print("\n--- GETITEM TEST ---")

    print(
        "account['user']:",
        account["user"],
    )

    print("\n--- SESSION TIMEOUT TEST ---")

    if account.session is not None:
        account.session.last_activity -= timedelta(
            seconds=901
        )

    print(
        "Authenticated after timeout:",
        account.is_authenticated(),
    )

    print("\n--- LOGIN AGAIN ---")

    account.login(
        username="Vadym",
        password="Qwerty123!",
        ip="192.168.1.10",
    )

    print(
        "Authenticated:",
        account.is_authenticated(),
    )

    print("\n--- LOGOUT ---")

    account.logout()

    print(
        "Authenticated after logout:",
        account.is_authenticated(),
    )

    print("\n--- AUDIT LOG ---")

    account.audit_log.show_all()


# Обробка команд demo та analyze
def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Laboratory work 2",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "demo",
        help="Run Task 1 demonstration",
    )

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze password dictionary",
    )

    analyze_parser.add_argument(
        "--wordlist",
        default=str(DEFAULT_WORDLIST),
        help="Path to password dictionary",
    )

    analyze_parser.add_argument(
        "--min-length",
        type=int,
        default=8,
        help="Minimum password length",
    )

    analyze_parser.add_argument(
        "--top-masks",
        type=int,
        default=5,
        help="Number of most common masks",
    )

    analyze_parser.add_argument(
        "--output-stats",
        default=str(DEFAULT_OUTPUT),
        help="Path to JSON report",
    )

    args = parser.parse_args()

    if args.command == "demo":
        run_demo()

    elif args.command == "analyze":
        try:
            run_analysis(
                wordlist=args.wordlist,
                min_length=args.min_length,
                top_masks=args.top_masks,
                output_stats=args.output_stats,
            )

        except (
            FileNotFoundError,
            ValueError,
            OSError,
        ) as error:
            logging.error(
                "%s",
                error,
            )


if __name__ == "__main__":
    main()