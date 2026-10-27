import os


class Settings:
    RECORDS_RETENTION_URL = os.environ.get(
        "RECORDS_RETENTION_URL", "https://records-retention.internal.example.invalid"
    )


settings = Settings()
