import random

from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

print(STUDENT_NAME)
print(GROUP_NAME)
print(VARIANT_NUMBER)


passwords = [
    "InfoS3c@2023",
    "simple123",
    "Def3ns3@Key",
    "public",
    "Encrypt3d#Pass",
    "basic123",
    "Secur3@Analysis",
    "temp123",
    "Pr0t3ct@Data",
    "default",
]

criteria = {
    "min_length": 8,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}

forbidden_passwords = {
    "simple123",
    "public",
    "basic123",
    "temp123",
    "default",
    "guest",
}


indices = random.sample(range(len(passwords)), 3)
duplicates = []

for index in indices:
    duplicates.append(passwords[index])

passwords.extend(duplicates)


def has_digit(password):
    return any(char.isdigit() for char in password)


def has_upper(password):
    return any(char.isupper() for char in password)


def has_special(password):
    return any(not char.isalnum() for char in password)


def has_lower(password):
    return any(char.islower() for char in password)


def is_long_enough(password):
    return len(password) >= criteria["min_length"]


def count_criteria(password):
    count = 0

    if is_long_enough(password):
        count += 1

    if has_digit(password):
        count += 1

    if has_upper(password):
        count += 1

    if has_special(password):
        count += 1

    return count


def is_forbidden(password):
    return password in forbidden_passwords or not is_long_enough(password)


def is_weak(password):
    if is_forbidden(password):
        return False

    return (
        has_digit(password)
        or has_upper(password)
        or has_special(password)
        or has_lower(password)
    )


def is_medium(password):
    if is_forbidden(password):
        return False

    count = count_criteria(password)

    return count >= 2 and count < 4


def is_strong(password):
    if is_forbidden(password):
        return False

    return (
        is_long_enough(password)
        and has_digit(password)
        and has_upper(password)
        and has_special(password)
        and len(password) <= criteria["min_length"] + 4
    )


def is_very_strong(password):
    if is_forbidden(password):
        return False

    return (
        is_long_enough(password)
        and has_digit(password)
        and has_upper(password)
        and has_special(password)
        and len(password) > criteria["min_length"] + 4
        and passwords.count(password) == 1
    )


def get_password_level(password):
    if is_very_strong(password):
        return "Very strong"

    if is_strong(password):
        return "Strong"

    if is_medium(password):
        return "Medium"

    if is_weak(password):
        return "Weak"

    return "Forbidden"


for password in passwords:
    level = get_password_level(password)
    print(password, "->", level)