from app.clients.retention import RetentionClient

ARCHIVING_ROLES = ("owner", "editor")

retention = RetentionClient()


def can_archive(viewer, shelf):
    if viewer.team_role not in ARCHIVING_ROLES:
        return False
    return not any(book.on_loan for book in shelf.books)


def can_purge(viewer, shelf):
    return retention.may_purge(team_id=shelf.team_id, shelf_id=shelf.id, requested_by=viewer.id)
