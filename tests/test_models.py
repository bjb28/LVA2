#!/usr/bin/env pytest -vs
"""Tests for Models for LVA2 API."""

# Standard Python Libraries
# Standard Libraries
from datetime import datetime

# Third-Party Libraries
import pytest
from rest_framework.serializers import ValidationError

# Custom Libraries
from api.models import Address, CollateralDuty, Member, SleepIn, StandBy

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestAddress:
    """Test Address model."""

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


@pytest.mark.django_db
class TestCollateralDuty:
    """Test Collateral Duty model."""

    pytestmark = pytest.mark.django_db

    def test_str(self):
        """Test proper str output."""
        assert (
            str(CollateralDuty.objects.filter(badge_num=12345).first())
            == "Collateral Duty: Doe, John 2023-10-02 10:00 - 2023-10-02 13:59"
        )

    @pytest.mark.parametrize(
        "end_time",
        [
            ("2023-10-02 13:30:00+00:00"),
            ("2023-10-02 10:30:00+00:00"),
            ("2023-10-02 11:00:00+00:00"),
        ],
    )
    def test_losap_false(self, end_time):
        """Test if losap_valid is false when less than min_hours."""
        collateralDuty_obj = CollateralDuty.objects.filter(badge_num=12345).first()
        collateralDuty_obj.end_time = datetime.fromisoformat(end_time)
        collateralDuty_obj.save()
        assert collateralDuty_obj.losap_valid is False

    @pytest.mark.parametrize(
        "start_time,end_time",
        [
            ("2023-10-01 06:00:00+00:00", "2023-10-01 09:59:00+00:00"),
            ("2023-10-01 14:00:00+00:00", "2023-10-01 18:00:00+00:00"),
            ("2023-10-02 15:00:00+00:00", "2023-10-02 18:59:00+00:00"),
        ],
    )
    def test_clean_standBy_pass(self, start_time, end_time):
        """Test Clean method focused on Stand By"""
        collateralDuty_obj = CollateralDuty.objects.filter(badge_num=12345).first()

        standBy_obj = StandBy.objects.filter(badge_num=12345).first()
        standBy_obj.start_time = datetime.fromisoformat(start_time)
        standBy_obj.end_time = datetime.fromisoformat(end_time)
        standBy_obj.save()

        collateralDuty_obj.clean()

    @pytest.mark.parametrize(
        "start_time,end_time",
        [
            ("2023-10-02 07:00:00+00:00", "2023-10-02 10:59:00+00:00"),
            ("2023-10-02 11:00:00+00:00", "2023-10-02 14:59:00+00:00"),
            ("2023-10-02 10:00:00+00:00", "2023-10-02 13:59:00+00:00"),
            ("2023-10-02 10:00:00+00:00", "2023-10-02 15:59:00+00:00"),
            ("2023-10-02 09:00:00+00:00", "2023-10-02 13:59:00+00:00"),
            ("2023-09-30 15:00:00+00:00", "2023-10-05 08:59:00+00:00"),
        ],
    )
    def test_clean_standBy_fail(self, start_time, end_time):
        """Test Clean method focused on Stand By"""
        collateralDuty_obj = CollateralDuty.objects.filter(badge_num=12345).first()

        standBy_obj = StandBy.objects.filter(badge_num=12345).first()
        standBy_obj.start_time = datetime.fromisoformat(start_time)
        standBy_obj.end_time = datetime.fromisoformat(end_time)
        standBy_obj.save()
        with pytest.raises(ValidationError):
            collateralDuty_obj.clean()

    @pytest.mark.parametrize(
        "start_time,end_time",
        [
            ("2023-10-02 15:00:00+00:00", "2023-10-02 18:59:00+00:00"),
            ("2023-10-03 06:00:00+00:00", "2023-10-03 09:59:00+00:00"),
            ("2023-10-03 15:00:00+00:00", "2023-10-03 18:59:00+00:00"),
        ],
    )
    def test_clean_sleepIn_pass(self, start_time, end_time):
        """Test Clean method focused on Sleep In"""
        collateralDuty_obj = CollateralDuty.objects.filter(badge_num=12345).first()
        collateralDuty_obj.start_time = datetime.fromisoformat(start_time)
        collateralDuty_obj.end_time = datetime.fromisoformat(end_time)
        collateralDuty_obj.clean()

    @pytest.mark.parametrize(
        "start_time,end_time",
        [
            ("2023-10-01 19:00:00+00:00", "2023-10-01 23:00:00+00:00"),
            ("2023-10-02 05:00:00+00:00", "2023-10-02 09:00:00+00:00"),
            ("2023-10-01 16:00:00+00:00", "2023-10-01 20:00:00+00:00"),
            ("2023-10-01 15:00:00+00:00", "2023-10-01 19:00:00+00:00"),
            ("2023-09-30 15:00:00+00:00", "2023-10-05 08:59:00+00:00"),
        ],
    )
    def test_clean_sleepIn_fail(self, start_time, end_time):
        """Test Clean method focused on Sleep In"""
        collateralDuty_obj = CollateralDuty.objects.filter(badge_num=12345).first()
        collateralDuty_obj.start_time = datetime.fromisoformat(start_time)
        collateralDuty_obj.end_time = datetime.fromisoformat(end_time)
        with pytest.raises(ValidationError):
            collateralDuty_obj.clean()

    @pytest.mark.parametrize(
        "start_time,end_time",
        [
            ("2023-10-02 07:00:00+00:00", "2023-10-02 10:59:00+00:00"),
            ("2023-10-02 11:00:00+00:00", "2023-10-02 14:59:00+00:00"),
            ("2023-10-02 09:00:00+00:00", "2023-10-02 18:59:00+00:00"),
            ("2023-10-01 15:00:00+00:00", "2023-10-05 08:59:00+00:00"),
        ],
    )
    def test_clean_collateralDuty_obj_fail(self, start_time, end_time):
        """Test Clean method focused on Collateral Duty."""
        collateralDuty_object = CollateralDuty(
            badge_num=Member(badge_num=12345, first_name="John", last_name="Doe"),
            start_time=start_time,
            end_time=end_time,
        )
        collateralDuty_object.start_time = datetime.fromisoformat(start_time)
        collateralDuty_object.end_time = datetime.fromisoformat(end_time)
        with pytest.raises(ValidationError):
            collateralDuty_object.clean()


@pytest.mark.django_db
class TestMember:
    """Test Member model."""

    pytestmark = pytest.mark.django_db

    def test_member_by_badge(self):
        mbr = Member.objects.filter(badge_num=12345)[0]
        assert mbr.badge_num == 12345

    def test_member_full_name(self, member_object):
        """Test proper string returned by full name method."""
        assert member_object.full_name() == "Doe, John"

    def test_member_full_member(self, member_object):
        """Test proper string returned by full member method."""
        assert member_object.full_member() == "Doe, John(12345)"


@pytest.mark.django_db
class TestSleepIn:
    """Test Sleep In model."""

    pytestmark = pytest.mark.django_db

    def test_str(self):
        """Test proper str output."""
        assert (
            str(SleepIn.objects.filter(badge_num=12345).first())
            == "Sleep In: Doe, John 2023-10-01"
        )

    @pytest.mark.parametrize(
        "start_time,end_time",
        [
            ("2023-10-01 15:00:00+00:00", "2023-10-01 18:59:00+00:00"),
            ("2023-10-02 07:00:00+00:00", "2023-10-02 11:00:00+00:00"),
            ("2023-10-03 19:00:00+00:00", "2023-10-03 23:00:00+00:00"),
        ],
    )
    def test_clean_collateralDuty_pass(self, start_time, end_time):
        """Test Clean method focused on Collateral Duty"""
        sleepIn_object = SleepIn.objects.filter(badge_num=12345).first()
        collateralDuty_obj = CollateralDuty.objects.filter(badge_num=12345).first()
        collateralDuty_obj.start_time = datetime.fromisoformat(start_time)
        collateralDuty_obj.end_time = datetime.fromisoformat(end_time)
        collateralDuty_obj.save()
        sleepIn_object.clean()

    @pytest.mark.parametrize(
        "start_time,end_time",
        [
            ("2023-10-01 19:00:00+00:00", "2023-10-01 23:00:00+00:00"),
            ("2023-10-02 05:00:00+00:00", "2023-10-02 09:00:00+00:00"),
            ("2023-10-01 16:00:00+00:00", "2023-10-01 20:00:00+00:00"),
            ("2023-10-01 15:00:00+00:00", "2023-10-01 19:00:00+00:00"),
            ("2023-09-30 15:00:00+00:00", "2023-10-03 08:59:00+00:00"),
        ],
    )
    def test_clean_collateralDuty_fail(self, start_time, end_time):
        """Test Clean method focused on Collateral Duty_"""
        sleepIn_object = SleepIn.objects.filter(badge_num=12345).first()
        collateralDuty_obj = CollateralDuty.objects.filter(badge_num=12345).first()
        collateralDuty_obj.start_time = datetime.fromisoformat(start_time)
        collateralDuty_obj.end_time = datetime.fromisoformat(end_time)
        collateralDuty_obj.save()
        with pytest.raises(ValidationError):
            sleepIn_object.badge_num = Member.objects.get(badge_num=12345)
            sleepIn_object.clean()

    @pytest.mark.parametrize(
        "start_time,end_time",
        [
            ("2023-10-01 15:00:00+00:00", "2023-10-01 18:59:00+00:00"),
            ("2023-10-02 07:00:00+00:00", "2023-10-02 11:00:00+00:00"),
            ("2023-10-03 19:00:00+00:00", "2023-10-03 23:00:00+00:00"),
        ],
    )
    def test_clean_standBy_pass(self, start_time, end_time):
        """Test Clean method focused on Stand By"""
        sleepIn_object = SleepIn.objects.filter(badge_num=12345).first()
        standBy_obj = StandBy.objects.filter(badge_num=12345).first()
        standBy_obj.start_time = datetime.fromisoformat(start_time)
        standBy_obj.end_time = datetime.fromisoformat(end_time)
        standBy_obj.save()
        sleepIn_object.clean()

    @pytest.mark.parametrize(
        "start_time,end_time",
        [
            ("2023-10-01 19:00:00+00:00", "2023-10-01 23:00:00+00:00"),
            ("2023-10-02 05:00:00+00:00", "2023-10-02 09:00:00+00:00"),
            ("2023-10-01 16:00:00+00:00", "2023-10-01 20:00:00+00:00"),
            ("2023-10-01 15:00:00+00:00", "2023-10-01 19:00:00+00:00"),
            ("2021-05-30 15:00:00+00:00", "2023-10-03 08:59:00+00:00"),
        ],
    )
    def test_clean_standBy_fail(self, start_time, end_time):
        """Test Clean method focused on Stand By"""
        sleepIn_object = SleepIn.objects.filter(badge_num=12345).first()
        standBy_obj = StandBy.objects.filter(badge_num=12345).first()
        standBy_obj.start_time = datetime.fromisoformat(start_time)
        standBy_obj.end_time = datetime.fromisoformat(end_time)
        standBy_obj.save()
        with pytest.raises(ValidationError):
            sleepIn_object.badge_num = Member.objects.get(badge_num=12345)
            sleepIn_object.clean()


@pytest.mark.django_db
class TestStandBy:
    """Test Stand By model."""

    pytestmark = pytest.mark.django_db

    def test_str(self):
        """Test proper str output."""
        assert (
            str(StandBy.objects.filter(badge_num=12345).first())
            == "Stand By: Doe, John 2023-10-03 10:00 - 2023-10-03 13:59"
        )

    @pytest.mark.parametrize(
        "start_time,end_time",
        [
            ("2023-10-01 06:00:00+00:00", "2023-10-01 09:59:00+00:00"),
            ("2023-10-01 14:00:00+00:00", "2023-10-01 18:00:00+00:00"),
            ("2023-10-02 15:00:00+00:00", "2023-10-02 18:59:00+00:00"),
        ],
    )
    def test_clean_collateralDuty_pass(self, start_time, end_time):
        """Test Clean method focused on Collateral Duty"""
        standBy_obj = StandBy.objects.filter(badge_num=12345).first()

        collateralDuty_obj = CollateralDuty.objects.filter(badge_num=12345).first()
        collateralDuty_obj.start_time = datetime.fromisoformat(start_time)
        collateralDuty_obj.end_time = datetime.fromisoformat(end_time)
        collateralDuty_obj.save()

        standBy_obj.clean()

    @pytest.mark.parametrize(
        "start_time,end_time",
        [
            ("2023-10-03 07:00:00+00:00", "2023-10-03 10:59:00+00:00"),
            ("2023-10-03 11:00:00+00:00", "2023-10-03 14:59:00+00:00"),
            ("2023-10-03 10:00:00+00:00", "2023-10-03 13:59:00+00:00"),
            ("2023-10-03 10:00:00+00:00", "2023-10-03 15:59:00+00:00"),
            ("2023-10-03 09:00:00+00:00", "2023-10-03 13:59:00+00:00"),
            ("2023-10-02 15:00:00+00:00", "2023-10-05 08:59:00+00:00"),
        ],
    )
    def test_clean_collateralDuty_fail(self, start_time, end_time):
        """Test Clean method focused on Sleep In"""
        standBy_obj = StandBy.objects.filter(badge_num=12345).first()

        collateralDuty_obj = CollateralDuty.objects.filter(badge_num=12345).first()
        collateralDuty_obj.start_time = datetime.fromisoformat(start_time)
        collateralDuty_obj.end_time = datetime.fromisoformat(end_time)
        collateralDuty_obj.save()
        with pytest.raises(ValidationError):
            standBy_obj.clean()

    @pytest.mark.parametrize(
        "start_time,end_time",
        [
            ("2023-10-01 15:00:00+00:00", "2023-10-01 18:59:00+00:00"),
            ("2023-10-03 07:00:00+00:00", "2023-10-03 11:00:00+00:00"),
            ("2023-10-03 15:00:00+00:00", "2023-10-03 18:59:00+00:00"),
        ],
    )
    def test_clean_sleepIn_pass(self, start_time, end_time):
        """Test Clean method focused on Sleep In"""
        standBy_obj = StandBy.objects.filter(badge_num=12345).first()
        standBy_obj.start_time = datetime.fromisoformat(start_time)
        standBy_obj.end_time = datetime.fromisoformat(end_time)
        standBy_obj.clean()

    @pytest.mark.parametrize(
        "start_time,end_time",
        [
            ("2023-10-01 19:00:00+00:00", "2023-10-01 23:00:00+00:00"),
            ("2023-10-02 05:00:00+00:00", "2023-10-02 09:00:00+00:00"),
            ("2023-10-01 16:00:00+00:00", "2023-10-01 20:00:00+00:00"),
            ("2023-10-01 15:00:00+00:00", "2023-10-01 19:00:00+00:00"),
            ("2023-09-30 15:00:00+00:00", "2023-10-05 08:59:00+00:00"),
        ],
    )
    def test_clean_sleepIn_fail(self, start_time, end_time):
        """Test Clean method focused on Sleep In"""
        standBy_obj = StandBy.objects.filter(badge_num=12345).first()
        standBy_obj.start_time = datetime.fromisoformat(start_time)
        standBy_obj.end_time = datetime.fromisoformat(end_time)
        with pytest.raises(ValidationError):
            standBy_obj.clean()

    @pytest.mark.parametrize(
        "start_time,end_time",
        [
            ("2023-10-03 07:00:00+00:00", "2023-10-03 10:59:00+00:00"),
            ("2023-10-03 11:00:00+00:00", "2023-10-03 14:59:00+00:00"),
            ("2023-10-03 09:00:00+00:00", "2023-10-03 18:59:00+00:00"),
            ("2023-10-02 15:00:00+00:00", "2023-10-06 08:59:00+00:00"),
        ],
    )
    def test_clean_standBy_fail(self, start_time, end_time):
        """Test Clean method focused on Stand By."""
        standBy_object = StandBy(
            badge_num=Member(badge_num=12345, first_name="John", last_name="Doe"),
            start_time="2023-10-01T10:00:00-00:00",
            end_time="2023-10-01T14:00:00-00:00",
        )
        standBy_object.start_time = datetime.fromisoformat(start_time)
        standBy_object.end_time = datetime.fromisoformat(end_time)

        with pytest.raises(ValidationError):
            standBy_object.clean()
