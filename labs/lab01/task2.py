from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

users = {
    "red_team_lead": {
        "role": "red_team",
        "clearance": 4,
        "department": "Red Team",
        "active": True,
    },
    "blue_team_analyst": {
        "role": "blue_team",
        "clearance": 3,
        "department": "Blue Team",
        "active": True,
    },
    "purple_team_coord": {
        "role": "purple_team",
        "clearance": 3,
        "department": "Purple Team",
        "active": True,
    },
    "student_intern": {
        "role": "student",
        "clearance": 1,
        "department": "Academia",
        "active": True,
    },
    "retired_expert": {
        "role": "retired",
        "clearance": 2,
        "department": "Emeritus",
        "active": False,
    },
}

resources = [
    ("attack_scenarios", 4),
    ("defense_playbooks", 3),
    ("exercise_plans", 3),
    ("research_papers", 1),
    ("exploit_tools", 4),
    ("student_resources", 1),
    ("simulation_results", 3),
    ("red_team_tools", 4),
    ("blue_team_reports", 3),
    ("public_research", 1),
]

security_levels = (
    "Academic",
    "Operational",
    "Tactical",
    "Strategic",
)

blocked_users = {
    "retired_expert",
    "academic_violator",
    "leaked_account",
}


def check_access(username, resource_level):
    if username not in users:
        return "DENY", "User not found"

    user = users[username]

    if username in blocked_users:
        return "DENY", "User is blocked"

    if not user["active"]:
        return "DENY", "Account inactive"

    if user["clearance"] >= resource_level:
        return "ALLOW", "Clearance OK"

    return "DENY", "Insufficient clearance"


def main():
    print(STUDENT_NAME)
    print(GROUP_NAME)
    print(VARIANT_NUMBER)

    print("\nResources:")
    for resource_name, level in resources:
        level_name = security_levels[level - 1]
        print(resource_name, "->", level_name)

    print("\nAccess check:")
    for username in users:
        for resource_name, resource_level in resources:
            result, reason = check_access(username, resource_level)

            print(
                f"user={username} "
                f"resource={resource_name} "
                f"-> {result} ({reason})"
            )


if __name__ == "__main__":
    main()