from typing import Any, Optional, Tuple, Type

try:
    import sqlglot  # type: ignore[import-untyped]
    from sqlglot import exp  # type: ignore[import-untyped]

    SQLGLOT_AVAILABLE = True
except ImportError:
    sqlglot = None  # type: ignore[assignment]
    exp = None  # type: ignore[assignment]
    SQLGLOT_AVAILABLE = False


class SqlPolicyError(Exception):
    pass


class SqlPolicyValidator:
    def validate(self, sql: str) -> Tuple[bool, str]:
        if not SQLGLOT_AVAILABLE or sqlglot is None:
            return (False, "ERROR: SQL validation library 'sqlglot' is not installed")

        try:
            self._validate_sql(sql)
            return (True, "VALID")
        except SqlPolicyError as e:
            return (False, f"ERROR: {str(e)}")

    def _validate_sql(self, sql: str) -> None:
        sql_clean: str = sql.strip().rstrip(";").strip()

        if not sql_clean:
            raise SqlPolicyError("Empty SQL query")

        if ";" in sql_clean:
            raise SqlPolicyError(
                "Multiple statements detected; only single queries allowed"
            )

        try:
            parsed: Any = sqlglot.parse_one(sql_clean, error_level=sqlglot.ErrorLevel.RAISE)  # type: ignore[attr-defined]
        except Exception as e:
            raise SqlPolicyError(f"Invalid SQL syntax: {str(e)}")

        if parsed is None:
            raise SqlPolicyError("Failed to parse SQL query")

        self._check_query_type(parsed)
        self._check_forbidden_operations(parsed)

    def _check_query_type(self, parsed: Any) -> None:
        if isinstance(parsed, exp.With):  # type: ignore[attr-defined]
            if parsed.this and isinstance(parsed.this, exp.Select):  # type: ignore[attr-defined]
                return
            raise SqlPolicyError("WITH clause must be followed by a SELECT statement")

        if isinstance(parsed, exp.Select):  # type: ignore[attr-defined]
            return

        explain_type: Optional[Type[Any]] = getattr(exp, "Explain", None)
        if explain_type and isinstance(parsed, explain_type):
            if parsed.this and isinstance(parsed.this, (exp.Select, exp.With)):  # type: ignore[attr-defined]
                return
            raise SqlPolicyError("EXPLAIN must be followed by a SELECT or WITH query")

        raise SqlPolicyError(
            f"Only SELECT, WITH + SELECT, and EXPLAIN queries are allowed. Found: {type(parsed).__name__}"
        )

    def _check_forbidden_operations(self, parsed: Any) -> None:
        forbidden_ops: list[str] = [
            "Insert",
            "Update",
            "Delete",
            "Drop",
            "AlterTable",
            "Alter",
            "Truncate",
            "Create",
            "Grant",
            "Revoke",
        ]

        forbidden_types: list[Type[Any]] = []
        for op_name in forbidden_ops:
            op_type: Optional[Type[Any]] = getattr(exp, op_name, None)
            if op_type is not None:
                forbidden_types.append(op_type)

        forbidden_tuple: tuple[Type[Any], ...] = tuple(forbidden_types)

        for node in parsed.walk():  # type: ignore[attr-defined]
            if isinstance(node, forbidden_tuple):
                operation: str = (
                    type(node).__name__.upper().replace("TABLE", "").strip()
                )
                raise SqlPolicyError(
                    f"Forbidden operation '{operation}' detected. Only read-only queries are permitted"
                )
