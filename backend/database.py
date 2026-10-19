
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "threatmeter.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS message_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                predicted_label TEXT NOT NULL,
                work_probability REAL,
                confidence TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # Safely add the SMS-specific column to an existing database.
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(message_history)"
            ).fetchall()
        }

        if "spam_probability" not in columns:
            connection.execute("""
                ALTER TABLE message_history
                ADD COLUMN spam_probability REAL
            """)


def save_analysis(message, result):
    if not isinstance(message, str):
        raise TypeError("Message must be text.")

    if not isinstance(result, dict):
        raise TypeError("Result must be a dictionary.")

    label = str(result["label"])
    confidence = str(result["confidence"])
    spam_probability = result.get("spam_probability")

    if spam_probability is not None:
        spam_probability = float(spam_probability)

        if not 0 <= spam_probability <= 1:
            raise ValueError(
                "spam_probability must be between 0 and 1."
            )

    # Retain the old field for compatibility with previous records.
    work_probability = None

    timestamp = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO message_history (
                message,
                predicted_label,
                work_probability,
                confidence,
                created_at,
                spam_probability
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            message,
            label,
            work_probability,
            confidence,
            timestamp,
            spam_probability
        ))

        return cursor.lastrowid


def get_recent_analyses(limit=20):
    limit = max(1, min(int(limit), 100))

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, message, predicted_label,
                   work_probability, spam_probability,
                   confidence, created_at
            FROM message_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(row) for row in rows]


if __name__ == "__main__":
    initialize_database()
    print("ThreatMeter database initialized successfully.")
    print(f"Database location: {DATABASE_FILE}")

    with get_connection() as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM message_history"
        ).fetchone()[0]

    print(f"Existing analysis records preserved: {count}")
