"""LVA2 API Tests."""
# Third-Party Libraries
from django.core.management import call_command
import pytest

# Custom Libraries
from api.models import Address, Member, Rank

""" Project Fixtures """


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up the django temp database."""
    with django_db_blocker.unblock():
        call_command("loaddata", "db/committee.json")
        call_command("loaddata", "db/hour_types.json")
        call_command("loaddata", "db/ranks.json")
        call_command("loaddata", "tests/test_db.json")


@pytest.fixture
def address_object_apt():
    """Return an Address Object."""
    return Address(
        street_num=1482, street_name="Main St", box_area="28-05", apt_num="A"
    )


@pytest.fixture
def address_object():
    """Return an Address Object."""
    return Address(street_num=1482, street_name="Annapolis Rd", box_area="28-01")


@pytest.fixture
def member_object():
    """Return a Member Object."""
    return Member(
        badge_num=12345,
        first_name="John",
        last_name="Doe",
        rank=Rank(abbr="FFII", is_officer=False, name="FireFighter 2"),
    )
