from pathlib import Path

import src.database as database


assert database.DATABASE_PATH != Path("data/docuagent.db")
assert "test" in database.DATABASE_PATH.name.lower()


print("Database path isolation tests passed.")
