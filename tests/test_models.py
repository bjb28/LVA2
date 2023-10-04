#!/usr/bin/env pytest -vs
"""Tests for Models."""

# Standard Python Libraries
# Standard Libraries
from datetime import datetime

# Third-Party Libraries
from django.core.exceptions import ValidationError
import pytest

# Custom Libraries
from api.models import Address, Member

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestMember:
    """Test Member model."""

    pytestmark = pytest.mark.django_db

    def test_address_str(self):
        assert (
            str(Address.objects.filter(street_name="Annapolis Rd").first())
            == "1482 Annapolis Rd(28-01)"
        )

    def test_address_str_apt(self):
        assert (
            str(Address.objects.filter(street_name="Main St").first())
            == "1482 Main St, A(28-05)"
        )

    def test_address_full(self):
        assert (
            Address.objects.filter(street_name="Annapolis Rd").first().full_address()
            == "1482 Annapolis Rd"
        )

    def test_address_full_apt(self):
        assert (
            Address.objects.filter(street_name="Main St").first().full_address()
            == "1482 Main St, A"
        )

    def test_member_by_badge(self):
        mbr = Member.objects.filter(badge_num=12345)[0]
        assert mbr.badge_num == 12345

    def test_member_full_name(self, member_object):
        """Test proper string returned by full name method."""
        assert member_object.full_name() == "Doe, John"

    def test_member_full_member(self, member_object):
        """Test proper string returned by full member method."""
        assert member_object.full_member() == "Doe, John(12345)"
