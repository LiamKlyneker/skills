import httpx

from app.settings import settings


class RetentionClient:
    """Client for the records-retention service, which owns every purge decision."""

    def __init__(self):
        self.base_url = settings.RECORDS_RETENTION_URL

    def may_purge(self, team_id, shelf_id, requested_by):
        response = httpx.get(
            f"{self.base_url}/v1/teams/{team_id}/shelves/{shelf_id}/purge-eligibility",
            params={"requested_by": requested_by},
        )
        response.raise_for_status()
        return response.json()["eligible"]
