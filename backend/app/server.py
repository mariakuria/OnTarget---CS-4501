"""Run the API with:  uvicorn app.server:build_app --factory"""
import os

from app.llm import default_llm
from app.main import create_app
from app.store import SqliteStore


def build_app():
    return create_app(llm=default_llm(), store=SqliteStore(os.environ.get("ONTARGET_DB", "ontarget.db")))
