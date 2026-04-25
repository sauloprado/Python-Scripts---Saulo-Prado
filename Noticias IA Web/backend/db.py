from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable


PROJECT_DIR = Path(__file__).resolve().parents[1]
STORAGE_DIR = PROJECT_DIR / "storage"
DB_DIR = STORAGE_DIR / "db"
DB_PATH = DB_DIR / "noticias_ia.db"
READINGS_DIR = STORAGE_DIR / "leituras"
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
PASSWORD_ITERATIONS = 260_000


def now_iso() -> str:
    return datetime.now().strftime(TIME_FORMAT)


def ensure_storage() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    READINGS_DIR.mkdir(parents=True, exist_ok=True)


def connect() -> sqlite3.Connection:
    ensure_storage()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generated_at TEXT NOT NULL,
                total_articles INTEGER NOT NULL,
                max_articles INTEGER NOT NULL,
                days_back INTEGER NOT NULL,
                topics TEXT NOT NULL,
                file_path TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                source TEXT NOT NULL,
                summary TEXT NOT NULL,
                image_url TEXT NOT NULL DEFAULT '',
                topic TEXT NOT NULL,
                published_at TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS run_articles (
                run_id INTEGER NOT NULL,
                article_id INTEGER NOT NULL,
                position INTEGER NOT NULL,
                PRIMARY KEY (run_id, article_id),
                FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE,
                FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
            );
            """
        )


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected = stored_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return secrets.compare_digest(digest, expected)


def create_default_user() -> None:
    username = os.getenv("APP_DEFAULT_USER", "saulo")
    password = os.getenv("APP_DEFAULT_PASSWORD", "trocar123")

    with connect() as conn:
        existing = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
        if existing:
            return

        conn.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, hash_password(password), now_iso()),
        )


def find_user_by_username(username: str) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()


def find_user_by_id(user_id: int) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute(
            "SELECT id, username, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()


def row_to_dict(row: sqlite3.Row) -> dict:
    return {key: row[key] for key in row.keys()}


def save_run(articles: Iterable[dict], options: dict, file_path: Path) -> int:
    article_list = list(articles)
    generated_at = now_iso()

    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO runs (generated_at, total_articles, max_articles, days_back, topics, file_path)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                generated_at,
                len(article_list),
                options["max_articles"],
                options["days_back"],
                ", ".join(options["topics"]),
                str(file_path.relative_to(PROJECT_DIR)),
            ),
        )
        run_id = int(cursor.lastrowid)

        for position, article in enumerate(article_list, start=1):
            now = now_iso()
            existing = conn.execute(
                "SELECT id FROM articles WHERE url = ?",
                (article["url"],),
            ).fetchone()

            if existing:
                article_id = int(existing["id"])
                conn.execute(
                    """
                    UPDATE articles
                    SET title = ?, source = ?, summary = ?, image_url = ?, topic = ?,
                        published_at = ?, last_seen_at = ?
                    WHERE id = ?
                    """,
                    (
                        article["title"],
                        article["source"],
                        article["summary"],
                        article.get("image_url", ""),
                        article["topic"],
                        article["published_at"],
                        now,
                        article_id,
                    ),
                )
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO articles (
                        title, url, source, summary, image_url, topic,
                        published_at, first_seen_at, last_seen_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        article["title"],
                        article["url"],
                        article["source"],
                        article["summary"],
                        article.get("image_url", ""),
                        article["topic"],
                        article["published_at"],
                        now,
                        now,
                    ),
                )
                article_id = int(cursor.lastrowid)

            conn.execute(
                "INSERT OR REPLACE INTO run_articles (run_id, article_id, position) VALUES (?, ?, ?)",
                (run_id, article_id, position),
            )

        return run_id


def list_runs(limit: int = 12) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, generated_at, total_articles, max_articles, days_back, topics, file_path
            FROM runs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [row_to_dict(row) for row in rows]


def latest_run() -> dict | None:
    runs = list_runs(limit=1)
    return runs[0] if runs else None


def list_articles(run_id: int | None = None) -> list[dict]:
    with connect() as conn:
        if run_id is None:
            run = conn.execute("SELECT id FROM runs ORDER BY id DESC LIMIT 1").fetchone()
            if not run:
                return []
            run_id = int(run["id"])

        rows = conn.execute(
            """
            SELECT
                a.id, a.title, a.url, a.source, a.summary, a.image_url,
                a.topic, a.published_at, ra.position
            FROM run_articles ra
            JOIN articles a ON a.id = ra.article_id
            WHERE ra.run_id = ?
            ORDER BY ra.position ASC
            """,
            (run_id,),
        ).fetchall()
        return [row_to_dict(row) for row in rows]


def bootstrap() -> None:
    init_db()
    create_default_user()
