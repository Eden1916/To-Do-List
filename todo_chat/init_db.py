"""Create missing database tables: python -m todo_chat.init_db."""

from todo_chat.config import Settings
from todo_chat.database import build_engine, init_database


def main():
    engine = build_engine(Settings().database_url)
    try:
        init_database(engine)
        print("Database initialized. Existing tables were preserved.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
