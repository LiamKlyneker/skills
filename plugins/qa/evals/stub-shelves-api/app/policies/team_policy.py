FREE_PLAN_SHELF_LIMIT = 5


def can_create_shelf(viewer, team):
    if team.plan == "paid":
        return True
    return len(team.shelves) < FREE_PLAN_SHELF_LIMIT
