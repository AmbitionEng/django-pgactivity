import ddf
import pytest
from django.db import connection

import pgactivity
from pgactivity.models import PGActivity


@pytest.mark.django_db
def test_context_percent_with_params():
    """A "%" in the context must not be treated as a placeholder"""
    with pgactivity.context(url="/%C0"):
        with connection.cursor() as cursor:
            cursor.execute("SELECT %s", [1])
            assert cursor.fetchone()[0] == 1

        # The ORM always passes params. The context that reaches the
        # database must not have a doubled "%"
        activity = PGActivity.objects.pid(pgactivity.pid()).get()
        assert activity.context == {"url": "/%C0"}


@pytest.mark.django_db
def test_context_percent_without_params():
    """A "%" in the context is sent as is when there are no params"""
    with pgactivity.context(url="/%C0"):
        with connection.cursor() as cursor:
            cursor.execute("SELECT query FROM pg_stat_activity WHERE pid = pg_backend_pid()")
            query = cursor.fetchone()[0]

    assert query.startswith('/*pga_context={"url": "/%C0"}*/\n')


@pytest.mark.django_db
def test_middleware_percent_in_url(client):
    """Requests with a "%" in the path do not break queries"""
    client.force_login(ddf.G("auth.User", is_staff=False))

    # Loading the user from the session issues queries with params.
    # Non-staff users are redirected to the admin login
    assert client.get("/admin/%C0/").status_code == 302
