from app.policies.shelf_policy import can_archive, can_purge
from app.policies.team_policy import can_create_shelf


def serialize_shelves(viewer, team):
    return {
        "viewer": {"can_create_shelf": can_create_shelf(viewer, team)},
        "shelves": [
            {
                "id": shelf.id,
                "name": shelf.name,
                "book_count": len(shelf.books),
                "archived_at": shelf.archived_at,
                "permissions": {
                    "can_archive": can_archive(viewer, shelf),
                    "can_purge": can_purge(viewer, shelf),
                },
            }
            for shelf in team.shelves
        ],
        "loans": [
            {"id": loan.id, "shelf_id": loan.shelf_id, "days_overdue": loan.days_overdue}
            for loan in team.loans
        ],
    }
