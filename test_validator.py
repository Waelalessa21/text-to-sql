import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "text_to_sql_engine" / "src"))

from ai_engine.core.sql_validator import SqlPolicyValidator


def test_validator():
    validator = SqlPolicyValidator()

    test_cases = [
        ("SELECT * FROM users", True, "Simple SELECT"),
        ("SELECT id, name FROM users WHERE age > 18", True, "SELECT with WHERE"),
        (
            "WITH cte AS (SELECT * FROM users) SELECT * FROM cte",
            True,
            "WITH + SELECT",
        ),
        ("EXPLAIN SELECT * FROM users", True, "EXPLAIN SELECT"),
        ("DELETE FROM users", False, "DELETE operation"),
        ("INSERT INTO users VALUES (1, 'test')", False, "INSERT operation"),
        ("UPDATE users SET name='test'", False, "UPDATE operation"),
        ("DROP TABLE users", False, "DROP operation"),
        ("CREATE TABLE test (id INT)", False, "CREATE operation"),
        ("ALTER TABLE users ADD COLUMN email TEXT", False, "ALTER operation"),
        ("TRUNCATE TABLE users", False, "TRUNCATE operation"),
        ("SELECT * FROM users; DROP TABLE users;", False, "Multiple statements"),
        ("", False, "Empty query"),
    ]

    print("SQL Policy Validator Tests\n")
    print("=" * 60)

    passed = 0
    failed = 0

    for sql, should_be_valid, description in test_cases:
        is_valid, message = validator.validate(sql)

        status = "PASS" if (is_valid == should_be_valid) else "FAIL"
        result = "PASS" if (is_valid == should_be_valid) else "FAIL"

        print(f"\n{status} {description}")
        print(f"   SQL: {sql[:50]}..." if len(sql) > 50 else f"   SQL: {sql}")
        print(f"   Result: {message}")

        if is_valid == should_be_valid:
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"\nResults: {passed} passed, {failed} failed out of {len(test_cases)} tests")

    if failed == 0:
        print("All tests passed!")
    else:
        print("Some tests failed")

    return failed == 0


if __name__ == "__main__":
    success = test_validator()
    sys.exit(0 if success else 1)
