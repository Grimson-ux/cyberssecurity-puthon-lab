import json
import logging
import re
from collections import Counter
from pathlib import Path
from typing import Iterator


logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_WORDLIST = DATA_DIR / "passwords.txt"
DEFAULT_OUTPUT = DATA_DIR / "mask_audit_report.json"


# Построкове читання словника паролів через генератор
def read_passwords(file_path: Path) -> Iterator[str]:
    with file_path.open(
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as file:
        for line in file:
            password = line.rstrip("\r\n")

            if password:
                yield password


# Визначення маски пароля за типами символів
def get_password_mask(password: str) -> str:
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[^A-Za-z0-9]", password))

    if has_lower and not has_upper and not has_digit and not has_special:
        return "LLLL"

    if has_digit and not has_upper and not has_lower and not has_special:
        return "dddd"

    if has_lower and has_digit and not has_upper and not has_special:
        return "LdLd"

    if has_upper and has_lower and has_digit and not has_special:
        return "UlLd"

    if has_upper and has_lower and has_digit and has_special:
        return "UlLdS"

    mask = ""

    if has_upper:
        mask += "U"

    if has_lower:
        mask += "L"

    if has_digit:
        mask += "d"

    if has_special:
        mask += "S"

    return mask or "Unknown"


# Аналіз словника та формування статистики
def analyze_wordlist(
    file_path: Path,
    min_length: int = 8,
    top_masks: int = 5,
) -> dict:
    if min_length <= 0:
        raise ValueError(
            "Minimum password length must be greater than 0."
        )

    if top_masks <= 0:
        raise ValueError(
            "Top masks value must be greater than 0."
        )

    if not file_path.exists():
        raise FileNotFoundError(
            f"Password dictionary not found: {file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Specified path is not a file: {file_path}"
        )

    total_passwords = 0
    weak_passwords = 0
    total_length = 0

    masks: Counter[str] = Counter()

    logger.info(
        "Processing password dictionary: %s",
        file_path,
    )

    for password in read_passwords(file_path):
        total_passwords += 1

        password_length = len(password)
        total_length += password_length

        if password_length < min_length:
            weak_passwords += 1

        password_mask = get_password_mask(password)
        masks[password_mask] += 1

        if total_passwords % 10_000 == 0:
            logger.info(
                "Analyzed %d passwords.",
                total_passwords,
            )

    logger.info(
        "Analyzed %d passwords.",
        total_passwords,
    )

    if total_passwords == 0:
        average_length = 0.0
        weak_percentage = 0.0

    else:
        average_length = total_length / total_passwords

        weak_percentage = (
            weak_passwords
            / total_passwords
            * 100
        )

    top_mask_list = []

    for mask, count in masks.most_common(top_masks):
        percentage = (
            count / total_passwords * 100
            if total_passwords
            else 0.0
        )

        top_mask_list.append(
            {
                "mask": mask,
                "count": count,
                "percentage": round(
                    percentage,
                    2,
                ),
            }
        )

    return {
        "total_passwords": total_passwords,
        "weak_passwords": weak_passwords,
        "weak_percentage": round(
            weak_percentage,
            2,
        ),
        "minimum_length": min_length,
        "average_length": round(
            average_length,
            2,
        ),
        "top_masks": top_mask_list,
    }


# Виведення результатів аналізу в консоль
def print_report(report: dict) -> None:
    print()
    print(
        "=== Password Dictionary Audit Summary ==="
    )

    print(
        "Total Passwords:",
        report["total_passwords"],
    )

    print(
        f"Weak Passwords "
        f"(<{report['minimum_length']}):",
        report["weak_passwords"],
        f"({report['weak_percentage']}%)",
    )

    print(
        "Average Length:",
        report["average_length"],
        "characters",
    )

    print()
    print(
        "=== Top Password Masks ==="
    )

    for number, item in enumerate(
        report["top_masks"],
        start=1,
    ):
        print(
            f"{number}. "
            f"{item['mask']} : "
            f"{item['count']} "
            f"({item['percentage']}%)"
        )


# Збереження статистики у JSON-файл
def save_report(
    report: dict,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
        )

    logger.info(
        "Dictionary statistics saved to %s",
        output_path,
    )


# Повний запуск аналізу словника паролів
def run_analysis(
    wordlist: str | None = None,
    min_length: int = 8,
    top_masks: int = 5,
    output_stats: str | None = None,
) -> None:
    if wordlist is None:
        wordlist_path = DEFAULT_WORDLIST
    else:
        wordlist_path = Path(wordlist)

    if output_stats is None:
        output_path = DEFAULT_OUTPUT
    else:
        output_path = Path(output_stats)

    report = analyze_wordlist(
        file_path=wordlist_path,
        min_length=min_length,
        top_masks=top_masks,
    )

    print_report(report)

    save_report(
        report=report,
        output_path=output_path,
    )