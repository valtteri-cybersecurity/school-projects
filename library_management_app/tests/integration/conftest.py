import os

import pymysql
import pytest


@pytest.fixture
def mysql_connections():

    if os.getenv("LIBRARY_TEST_MYSQL") != "1":
        pytest.skip(
            "Set LIBRARY_TEST_MYSQL=1 to run real MySQL tests"
        )

    host = os.getenv("LIBRARY_TEST_MYSQL_HOST", "127.0.0.1")

    if host != "127.0.0.1":
        pytest.fail(
            "Integration tests only support local MySQL at 127.0.0.1"
        )

    user = os.getenv("LIBRARY_TEST_MYSQL_USER")
    password = os.getenv("LIBRARY_TEST_MYSQL_PASSWORD")

    if not user or password is None:
        pytest.fail(
            "Set LIBRARY_TEST_MYSQL_USER and "
            "LIBRARY_TEST_MYSQL_PASSWORD"
        )

    port = int(os.getenv("LIBRARY_TEST_MYSQL_PORT", "3306"))

    settings = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "charset": "utf8mb4",
        "connect_timeout": 5,
    }

    admin = pymysql.connect(**settings, autocommit=True)

    database_name = "library_migration_test_db"

    created = False
    connections = []

    try:
        with admin.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE `{database_name}` "
                "CHARACTER SET utf8mb4"
            )

        created = True

        for number in range(2):
            connection = pymysql.connect(
                **settings,
                database=database_name,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
            )

            connections.append(connection)

        yield connections[0], connections[1]

    finally:
        for connection in connections:
            connection.close()

        if created:
            with admin.cursor() as cursor:
                cursor.execute(
                    f"DROP DATABASE `{database_name}`"
                )

        admin.close()
