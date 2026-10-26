
import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).parent / "usage_limits.db"


def initialize_database():
    """Create the usage tracking table if it does not exist."""
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS usage (
                user_id TEXT NOT NULL,
                usage_date TEXT NOT NULL,
                request_count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, usage_date)
            )
            """
        )


def get_usage(user_id: str) -> int:
    """Return the number of requests used today."""
    today = date.today().isoformat()

    with sqlite3.connect(DB_PATH) as connection:
        result = connection.execute(
            """
            SELECT request_count
            FROM usage
            WHERE user_id = ? AND usage_date = ?
            """,
            (user_id, today),
        ).fetchone()

    return result[0] if result else 0


def check_and_record_usage(
    user_id: str,
    daily_limit: int = 5,
) -> tuple[bool, int]:
    """
    Check whether a user can make another request.

    Returns:
        (allowed, remaining_requests)
    """
    today = date.today().isoformat()

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("BEGIN IMMEDIATE")

        result = connection.execute(
            """
            SELECT request_count
            FROM usage
            WHERE user_id = ? AND usage_date = ?
            """,
            (user_id, today),
        ).fetchone()

        current_count = result[0] if result else 0

        if current_count >= daily_limit:
            connection.commit()
            return False, 0

        new_count = current_count + 1

        connection.execute(
            """
            INSERT INTO usage (user_id, usage_date, request_count)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, usage_date)
            DO UPDATE SET request_count = excluded.request_count
            """,
            (user_id, today, new_count),
        )

        connection.commit()

    return True, daily_limit - new_count


initialize_database()
