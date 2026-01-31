from typing import List, Tuple


class SupportedDatabaseTypes:
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"

    @classmethod
    def all(cls) -> List[str]:
        return [cls.SQLITE, cls.POSTGRESQL, cls.MYSQL]

    @classmethod
    def placeholder_for(cls, db_type: str) -> str:
        placeholders = {
            cls.SQLITE: "sqlite:///path/to/file.db",
            cls.POSTGRESQL: "postgresql://user:pass@host:5432/dbname",
            cls.MYSQL: "mysql+pymysql://user:pass@host:3306/dbname",
        }
        return placeholders.get(db_type, "connection_url")
