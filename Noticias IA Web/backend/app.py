from __future__ import annotations

import os
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, session
from werkzeug.exceptions import HTTPException

import db
from news_service import NewsOptions, fetch_news, save_reading_file


PROJECT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIST = PROJECT_DIR / "frontend" / "dist"


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    app.secret_key = os.getenv("APP_SECRET_KEY", "noticias-ia-web-dev-secret")
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    db.bootstrap()

    @app.errorhandler(Exception)
    def handle_error(error: Exception):
        if isinstance(error, HTTPException):
            return jsonify({"error": error.description}), error.code

        app.logger.exception(error)
        return jsonify({"error": str(error)}), 500

    def read_int(value, default: int, minimum: int, maximum: int) -> int:
        try:
            number = int(value)
        except (TypeError, ValueError):
            number = default

        return max(minimum, min(number, maximum))

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                return jsonify({"error": "Autenticacao necessaria."}), 401
            return view(*args, **kwargs)

        return wrapped

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True})

    @app.post("/api/auth/login")
    def login():
        payload = request.get_json(silent=True) or {}
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", ""))

        user = db.find_user_by_username(username)
        if not user or not db.verify_password(password, user["password_hash"]):
            return jsonify({"error": "Usuario ou senha invalidos."}), 401

        session.clear()
        session["user_id"] = int(user["id"])
        session["username"] = user["username"]
        return jsonify({"user": {"id": int(user["id"]), "username": user["username"]}})

    @app.post("/api/auth/logout")
    def logout():
        session.clear()
        return jsonify({"ok": True})

    @app.get("/api/auth/me")
    def me():
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"user": None})

        user = db.find_user_by_id(int(user_id))
        if not user:
            session.clear()
            return jsonify({"user": None})

        return jsonify({"user": {"id": int(user["id"]), "username": user["username"]}})

    @app.get("/api/news")
    @login_required
    def list_news():
        run_id = request.args.get("run_id", type=int)
        run = db.latest_run() if run_id is None else None
        articles = db.list_articles(run_id=run_id)
        return jsonify({"run": run, "articles": articles})

    @app.post("/api/news/generate")
    @login_required
    def generate_news():
        payload = request.get_json(silent=True) or {}
        topics_value = payload.get("topics", "")
        topics = (
            [topic.strip() for topic in topics_value.split(",") if topic.strip()]
            if isinstance(topics_value, str)
            else []
        )
        options = NewsOptions(
            max_articles=read_int(payload.get("max_articles"), 12, 1, 30),
            days_back=read_int(payload.get("days_back"), 1, 1, 7),
            topics=topics,
        )

        articles = fetch_news(options)
        if not articles:
            return jsonify({"error": "Nenhuma noticia recente encontrada."}), 404

        file_path = save_reading_file(articles, options)
        run_id = db.save_run(
            articles,
            {
                "max_articles": options.max_articles,
                "days_back": options.days_back,
                "topics": options.normalized_topics(),
            },
            file_path,
        )

        return jsonify(
            {
                "run": db.latest_run(),
                "articles": db.list_articles(run_id=run_id),
            }
        )

    @app.get("/api/runs")
    @login_required
    def runs():
        return jsonify({"runs": db.list_runs()})

    @app.get("/api/files/<path:filename>")
    @login_required
    def file_download(filename: str):
        return send_from_directory(db.READINGS_DIR, filename, as_attachment=True)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path: str):
        if FRONTEND_DIST.exists():
            requested = FRONTEND_DIST / path
            if path and requested.exists():
                return send_from_directory(FRONTEND_DIST, path)
            return send_from_directory(FRONTEND_DIST, "index.html")
        return jsonify({"message": "Frontend ainda nao foi compilado."})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5051, debug=os.getenv("FLASK_DEBUG") == "1")
