
from contextlib import contextmanager
import hashlib


def get_lock_name(connection) -> str:
    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE() AS db_name")
        result = cursor.fetchone()

    if result is None or not result["db_name"]:
        raise RuntimeError("No database selected!")

    database_name = result["db_name"]

    database_hash = hashlib.sha256(
        database_name.encode("utf-8")
    ).hexdigest()[:32]

    return f"library_migration_{database_hash}"


@contextmanager
def migration_lock(connection, timeout: int = 10):

    if not isinstance(timeout, int) or isinstance(timeout, bool):
        raise ValueError("Lock timeout must be an integer!")

    if timeout < 0:
        raise ValueError("Lock timeout cannot be negative!")

    lock_name = get_lock_name(connection)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT GET_LOCK(%s, %s) AS acquired",
            (lock_name, timeout)
        )

        result = cursor.fetchone()

    if result is None or result["acquired"] != 1:
        raise RuntimeError(
            f"Unable to acquire migration lock: {lock_name}"
        )

    try:
        yield

    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT RELEASE_LOCK(%s) AS released",
                (lock_name,)
            )

            result = cursor.fetchone()

        if result is None or result["released"] != 1:
            raise RuntimeError(
                f"Unable to release migration lock: {lock_name}"
            )
