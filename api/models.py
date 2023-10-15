"""Models to LVA2."""

# Standard Python Libraries
from datetime import datetime, timedelta

# Third-Party Libraries
from django.conf import settings
from django.db import models
import pytz
from rest_framework.serializers import ValidationError


class Address(models.Model):
    """
    Represents an address in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        street_num (models.IntegerField): The street number of the address.
        street_name (models.CharField): The name of the street.
        box_area (models.CharField): The box or area associated with the address.
        apt_num (models.CharField): The apartment number (optional).

    Meta:
        managed (bool): Indicates whether this model is managed by Django's database
            migrations.
        db_table (str): The name of the database table for this model.
        models.UniqueConstraint: Ensures the uniqueness of the combination of street_num,
            street_name, and apt_num.
        ordering (list of str): The default ordering for querysets of this model, first
            ordered by 'box_area' and then by 'street_name'.

    Example:
        To create a new address:

        ```python
        address = Address.objects.create(
            street_num=123,
            street_name="Main St",
            box_area="Box A",
            apt_num="Apt 101"
        )
        ```

    Methods:
        __str__(): Return a string address with box area.
        full_address(): Return a string of the full street address.

    """

    street_num = models.IntegerField(db_column="StreetNum")
    street_name = models.CharField(db_column="StreetName", max_length=100)
    box_area = models.CharField(db_column="BoxArea", max_length=10)
    apt_num = models.CharField(db_column="AptNum", max_length=20, blank=True, null=True)

    class Meta:
        """Meta data of Address."""

        db_table = "Address"
        models.UniqueConstraint(
            fields=["street_num", "street_name", "apt_num"], name="unique_address"
        )
        ordering = ["box_area", "street_name"]

    def __str__(self):
        """Return a string address with box area."""
        if self.apt_num:
            return (
                f"{self.street_num} {self.street_name}, {self.apt_num}({self.box_area})"
            )
        else:
            return f"{self.street_num} {self.street_name}({self.box_area})"

    def full_address(self):
        """Return a string of the full street address."""
        if self.apt_num:
            return f"{self.street_num} {self.street_name}, {self.apt_num}"
        else:
            return f"{self.street_num} {self.street_name}"


class CollateralDuty(models.Model):
    """
    Represents a collateral duty entry in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        start_time (models.DateTimeField): The start time of the collateral duty.
        end_time (models.DateTimeField): The end time of the collateral duty.
        type (models.ForeignKey): The type of collateral duty (HourType).
        committee (models.ForeignKey): The committee associated with the duty (Committee).
        description (models.CharField): A description of the duty.
        badge_num (models.ForeignKey): The member (BadgeNum) responsible for the duty.
        losap_valid (models.BooleanField): Indicates if the duty counts for LOSAP.

    Meta:
        db_table (str): The name of the database table for this model.
        verbose_name (str): A human-readable name for this model.

    Methods:
        __str__(): Returns a formatted string representation of the collateral duty.
        save(): Updates the collateral duty to check if it counts for LOSAP.
        clean(): Validates that the collateral duty does not overlap with other entities.

    """

    start_time = models.DateTimeField(db_column="StartTime")
    end_time = models.DateTimeField(db_column="EndTime")
    type = models.ForeignKey("HourType", on_delete=models.RESTRICT, db_column="Type")
    committee = models.ForeignKey(
        "Committee", on_delete=models.RESTRICT, db_column="Committee"
    )
    description = models.CharField(db_column="Description", max_length=120)
    badge_num = models.ForeignKey(
        "Member",
        on_delete=models.CASCADE,
        db_column="BadgeNum",
        related_name="collateralduty",
    )
    losap_valid = models.BooleanField(db_column="LOSAPValid", default=False)

    class Meta:
        """Meta data of Collateral Duty."""

        db_table = "CollateralDuty"
        verbose_name = "Collateral Duty"

    def __str__(self):
        """Return a string representation of collateral duty."""
        return (
            f"{type(self)._meta.verbose_name}: {self.badge_num.full_name()}"
            + f" {self.start_time.strftime('%Y-%m-%d %H:%M')} -"
            + f" {self.end_time.strftime('%Y-%m-%d %H:%M')}"
        )

    def save(self, *args, **kwargs):
        """Save to check if the Collateral Duty counts for LOSAP."""
        time_diff = self.end_time - self.start_time

        min_seconds = (self.type.min_hours * 3600) - 60

        if time_diff.total_seconds() >= min_seconds:
            self.losap_valid = True
        else:
            self.losap_valid = False

        super().save(*args, **kwargs)

    def clean(self):
        """Validate Collateral Duty does not overlap with other entities."""
        for sleepIn in SleepIn.objects.filter(badge_num=self.badge_num):
            sleepIn_start_time = datetime(
                sleepIn.date.year, sleepIn.date.month, sleepIn.date.day
            ).replace(hour=19, minute=0, tzinfo=pytz.timezone(settings.TIME_ZONE))
            sleepIn_end_time = datetime(
                sleepIn.date.year, sleepIn.date.month, sleepIn.date.day
            ).replace(
                hour=6, minute=59, tzinfo=pytz.timezone(settings.TIME_ZONE)
            ) + timedelta(
                days=1
            )
            if (
                (
                    self.start_time >= sleepIn_start_time
                    and self.start_time <= sleepIn_end_time
                )
                or (
                    self.end_time >= sleepIn_start_time
                    and self.end_time < sleepIn_end_time
                )
                or (
                    self.start_time <= sleepIn_end_time
                    and self.end_time >= sleepIn_start_time
                )
            ):
                raise ValidationError(
                    {
                        "message": (
                            f"{type(self)._meta.verbose_name} cannot overlap"
                            + " with a Sleep In."
                        )
                    }
                )

        if (
            StandBy.objects.filter(
                badge_num=self.badge_num,
                start_time__gte=self.start_time,
                start_time__lte=self.end_time,
            ).count()
            or StandBy.objects.filter(
                badge_num=self.badge_num,
                end_time__gte=self.start_time,
                end_time__lt=self.end_time,
            ).count()
            or StandBy.objects.filter(
                badge_num=self.badge_num,
                start_time__lte=self.end_time,
                end_time__gte=self.start_time,
            ).count()
        ):
            raise ValidationError(
                {
                    "message": (
                        f"{type(self)._meta.verbose_name} cannot overlap with"
                        + " a Stand By."
                    )
                }
            )
        elif (
            CollateralDuty.objects.filter(
                badge_num=self.badge_num,
                start_time__gte=self.start_time,
                start_time__lte=self.end_time,
            )
            .exclude(pk=self.pk)
            .count()
            or CollateralDuty.objects.filter(
                badge_num=self.badge_num,
                end_time__gte=self.start_time,
                end_time__lt=self.end_time,
            )
            .exclude(pk=self.pk)
            .count()
            or CollateralDuty.objects.filter(
                badge_num=self.badge_num,
                start_time__lte=self.end_time,
                end_time__gte=self.start_time,
            )
            .exclude(pk=self.pk)
            .count()
        ):
            raise ValidationError(
                {
                    "message": (
                        f"{type(self)._meta.verbose_name} cannot overlap with"
                        + " a Collateral Duty."
                    )
                }
            )


class Committee(models.Model):
    """
    Represents a committee in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        name (models.CharField): The name of the committee (Primary Key).

    Meta:
        db_table (str): The name of the database table for this model.

    Example:
        To create a new committee:

        ```python
        committee = Committee.objects.create(name="Finance Committee")
        ```

    Note:
        This model defines committees in the database, and the 'name' field serves as the primary key.

    """

    name = models.CharField(db_column="Name", primary_key=True, max_length=50)

    class Meta:
        """Meta data of Committee."""

        db_table = "Committee"


class CourseCode(models.Model):
    """
    Represents a course code in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        code (models.CharField): The course code (Primary Key).
        name (models.CharField): The name or description of the course.

    Meta:
        db_table (str): The name of the database table for this model.

    Example:
        To create a new course code:

        ```python
        course_code = CourseCode.objects.create(code="CS101", name="Introduction to Computer Science")
        ```

    Note:
        This model stores information about course codes, with 'code' as the primary key.

    """

    code = models.CharField(db_column="Code", primary_key=True, max_length=6)
    name = models.CharField(db_column="Name", max_length=50)

    class Meta:
        """Meta data of Course Code."""

        db_table = "CourseCode"


class HourType(models.Model):
    """
    Represents an hour type in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        name (models.CharField): The name of the hour type (Primary Key).
        min_hours (models.IntegerField): The minimum number of hours for this type (optional).

    Meta:
        db_table (str): The name of the database table for this model.

    Example:
        To create a new hour type:

        ```python
        hour_type = HourType.objects.create(name="Regular", min_hours=40)
        ```

    Note:
        This model stores information about hour types, with 'name' as the primary key.
        The 'min_hours' field can be used to specify a minimum required number of hours for this type.

    """

    name = models.CharField(db_column="Name", primary_key=True, max_length=20)
    min_hours = models.IntegerField(db_column="MinHours", blank=True, null=True)

    class Meta:
        """Meta data of Hour Type."""

        db_table = "HourType"


class Incident(models.Model):
    """
    Represents an incident in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        incident_num (models.IntegerField): The incident number (Primary Key).
        address (models.ForeignKey): The associated address of the incident (Address).
        incidentType (models.CharField): The type of incident (e.g., "Fire," "Medical").
        officer (models.IntegerField): The ID of the responding officer (optional).
        dispatch_time (models.DateTimeField): The time when the incident was dispatched.
        cleared_time (models.DateTimeField): The time when the incident was cleared (optional).
        created_time (models.DateTimeField): The timestamp when the incident was created (optional).
        updated_time (models.DateTimeField): The timestamp when the incident was last updated (optional).

    Meta:
        db_table (str): The name of the database table for this model.

    Example:
        To create a new incident:

        ```python
        incident = Incident.objects.create(
            incident_num=12345,
            address=address_instance,
            incidentType="Fire",
            officer=officer_id,
            dispatch_time=datetime.now(),
            cleared_time=datetime.now(),
            created_time=datetime.now(),
            updated_time=datetime.now(),
        )
        ```

    Note:
        This model represents incidents, with 'incident_num' as the primary key.
        The 'officer' field is optional and can be used to record the ID of the responding officer.

    """

    incident_num = models.IntegerField(db_column="IncidentNum", primary_key=True)
    address = models.ForeignKey(Address, models.RESTRICT, db_column="Address")
    incidentType = models.CharField(
        db_column="IncidentType", max_length=10, blank=True, null=True
    )
    officer = models.IntegerField(db_column="Officer", blank=True, null=True)
    dispatch_time = models.DateTimeField(db_column="DispatchTime")
    cleared_time = models.DateTimeField(db_column="ClearedTime", blank=True, null=True)
    created_time = models.DateTimeField(db_column="CreatedTime", blank=True, null=True)
    updated_time = models.DateTimeField(db_column="UpdatedTime", blank=True, null=True)

    class Meta:
        """Meta data of Incident."""

        db_table = "Incident"


class MemberResponse(models.Model):
    """
    Represents a member's response on a unit with a specific incident in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        badge_num (models.OneToOneField): The member's badge number (Primary Key).
        unit (models.ForeignKey): The unit to which the member responded (UnitResponse).
        rank_at_time (models.CharField): The member's rank at the time of response (optional).

    Meta:
        db_table (str): The name of the database table for this model.
        models.UniqueConstraint: Ensures the uniqueness of the combination of incident, call_sign, and badge_num.
        ordering (list of str): The default ordering for querysets of this model.

    Example:
        To create a new member response:

        ```python
        member_response = MemberResponse.objects.create(
            badge_num=member_instance,
            unit=unit_response_instance,
            rank_at_time="Captain"
        )
        ```

    Note:
        This model represents member responses to units. The combination of incident,
        call_sign, and badge_num is unique.

    """

    badge_num = models.OneToOneField(
        "Member", models.CASCADE, db_column="BadgeNum", primary_key=True
    )
    unit = models.ForeignKey(
        "UnitResponse",
        models.CASCADE,
        db_column="Unit",
        related_name="memberresponse_unit_set",
    )
    rank_at_time = models.CharField(
        db_column="RankAtTime", max_length=10, blank=True, null=True
    )

    class Meta:
        """Meta data of Member Response."""

        db_table = "MemberResponse"
        models.UniqueConstraint(
            fields=["unit__incident_num", "unit__call_sign", "badge_num"],
            name="unique_mbr_response",
        )
        ordering = ["unit__incident_num", "unit__call_sign", "badge_num"]


class MemberTrainingReport(models.Model):
    """
    Represents a member's training report in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        badge_num (models.OneToOneField): The member's badge number (Primary Key).
        training_report (models.ForeignKey): The associated training report (TrainingReport).

    Meta:
        db_table (str): The name of the database table for this model.
        models.UniqueConstraint: Ensures the uniqueness of the combination of training_report and badge_num.
        ordering (list of str): The default ordering for querysets of this model.

    Example:
        To create a new member training report:

        ```python
        member_training_report = MemberTrainingReport.objects.create(
            badge_num=member_instance,
            training_report=training_report_instance
        )
        ```

    Note:
        This model represents a link between members and their associated training reports.
        The combination of training_report and badge_num is unique.

    """

    badge_num = models.OneToOneField(
        "Member", models.CASCADE, db_column="BadgeNum", primary_key=True
    )
    training_report = models.ForeignKey(
        "TrainingReport", models.CASCADE, db_column="TrainingReport"
    )

    class Meta:
        """Meta data of Member Training Report."""

        db_table = "MemberTrainingReport"
        models.UniqueConstraint(
            fields=["training_report", "badge_num"], name="unique_training_report"
        )
        ordering = ["training_report", "badge_num"]


class Member(models.Model):
    """
    Represents a member in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        badge_num (models.IntegerField): The member's badge number (Primary Key).
        first_name (models.CharField): The first name of the member.
        last_name (models.CharField): The last name of the member.
        rank (models.ForeignKey): The member's rank (Rank).
        created (models.DateTimeField): The timestamp when the member was created (auto-generated).
        updated (models.DateTimeField): The timestamp when the member was last updated (auto-generated).

    Meta:
        db_table (str): The name of the database table for this model.
        models.UniqueConstraint: Ensures the uniqueness of the combination of badge_num, first_name, and last_name.

    Example:
        To create a new member:

        ```python
        member = Member.objects.create(
            badge_num=123,
            first_name="John",
            last_name="Doe",
            rank=rank_instance
        )
        ```

    Note:
        This model represents members with 'badge_num' as the primary key.
        The 'created' and 'updated' fields are auto-generated timestamps.

    """

    badge_num = models.IntegerField(db_column="BadgeNum", primary_key=True)
    first_name = models.CharField(db_column="FirstName", max_length=50)
    last_name = models.CharField(db_column="LastName", max_length=50)
    rank = models.ForeignKey("Rank", models.RESTRICT, db_column="Rank")
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta data of Member."""

        db_table = "Member"
        models.UniqueConstraint(
            fields=["badge_num", "first_name", "last_name"], name="unique_member"
        )

    def full_name(self):
        """Return a string of the last name, first name of the member."""
        return f"{self.last_name}, {self.first_name}"

    def full_member(self):
        """Return a string of the last name, first name(badge number)."""
        return f"{self.last_name}, {self.first_name}({self.badge_num})"


class Rank(models.Model):
    """
    Represents a rank in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        abbr (models.CharField): The abbreviation of the rank (Primary Key).
        is_officer (models.IntegerField): Indicates whether the rank is for an officer (0 for no, 1 for yes).
        name (models.CharField): The full name or description of the rank.

    Meta:
        db_table (str): The name of the database table for this model.

    Example:
        To create a new rank:

        ```python
        rank = Rank.objects.create(abbr="LT", is_officer=1, name="Lieutenant")
        ```

    Note:
        This model represents ranks, with 'abbr' as the primary key. The 'is_officer' field
        indicates whether the rank is for an officer (0 for no, 1 for yes).

    """

    abbr = models.CharField(db_column="Abbr", primary_key=True, max_length=10)
    is_officer = models.IntegerField(db_column="IsOfficer")
    name = models.CharField(db_column="Name", max_length=100)

    class Meta:
        """Meta data of Rank."""

        db_table = "Rank"

    def __str__(self):
        """Return a string representation of Rank."""
        return f"""{self.abbr} - {self.name}"""


class SleepIn(models.Model):
    """
    Represents a sleep-in record in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        date (models.DateTimeField): The date of the sleep-in.
        type (models.ForeignKey): The type of hours associated with the sleep-in (HourType).
        badge_num (models.ForeignKey): The member's badge number (Member).

    Meta:
        db_table (str): The name of the database table for this model.
        verbose_name (str): The human-readable name of the model.
        models.UniqueConstraint: Ensures the uniqueness of the combination of badge_num and date.

    Example:
        To create a new sleep-in record:

        ```python
        sleep_in = SleepIn.objects.create(
            date=datetime.now(),
            type=hour_type_instance,
            badge_num=member_instance
        )
        ```

    Note:
        This model represents sleep-in records, with 'date' as the primary key. Sleep-in records are
        associated with a member and a type of hours (e.g., "Regular" or "Overtime").

    """

    date = models.DateTimeField(db_column="Date")
    type = models.ForeignKey(HourType, models.RESTRICT, db_column="Type")
    badge_num = models.ForeignKey(
        Member, models.CASCADE, db_column="BadgeNum", related_name="sleepin"
    )

    class Meta:
        """Meta data of Sleep In."""

        db_table = "SleepIn"
        verbose_name = "Sleep In"
        models.UniqueConstraint(fields=["badge_num", "date"], name="unique_sleep_in")

    def __str__(self):
        """Return a string representation of a Sleep In."""
        return f"""{type(self)._meta.verbose_name}: {self.badge_num.full_name()} {self.date.strftime('%Y-%m-%d')}"""

    def clean(self):
        """Validate Sleep In does not overlap with other entities."""
        sleepIn_start_time = self.date.replace(
            hour=19, minute=0, tzinfo=pytz.timezone(settings.TIME_ZONE)
        )
        sleepIn_end_time = self.date.replace(
            hour=6, minute=59, tzinfo=pytz.timezone(settings.TIME_ZONE)
        ) + timedelta(days=1)

        if SleepIn.objects.filter(badge_num=self.badge_num, date=self.date).count():
            raise ValidationError(
                {
                    "message": (
                        f"{type(self)._meta.verbose_name} cannot be the same day as"
                        + " another Sleep In."
                    )
                }
            )
        elif (
            StandBy.objects.filter(
                badge_num=self.badge_num,
                start_time__gte=sleepIn_start_time,
                start_time__lte=sleepIn_end_time,
            ).count()
            or StandBy.objects.filter(
                badge_num=self.badge_num,
                end_time__gte=sleepIn_start_time,
                end_time__lt=sleepIn_end_time,
            ).count()
            or StandBy.objects.filter(
                badge_num=self.badge_num,
                start_time__lte=sleepIn_end_time,
                end_time__gte=sleepIn_start_time,
            ).count()
        ):
            raise ValidationError(
                {
                    "message": (
                        f"{type(self)._meta.verbose_name} cannot overlap with"
                        + " a Stand By."
                    )
                }
            )
        elif (
            CollateralDuty.objects.filter(
                badge_num=self.badge_num,
                start_time__gte=sleepIn_start_time,
                start_time__lte=sleepIn_end_time,
            ).count()
            or CollateralDuty.objects.filter(
                badge_num=self.badge_num,
                end_time__gte=sleepIn_start_time,
                end_time__lt=sleepIn_end_time,
            ).count()
            or CollateralDuty.objects.filter(
                badge_num=self.badge_num,
                start_time__lte=sleepIn_end_time,
                end_time__gte=sleepIn_start_time,
            ).count()
        ):
            raise ValidationError(
                {
                    "message": (
                        f"{type(self)._meta.verbose_name} cannot overlap with"
                        + " a Collateral Duty."
                    )
                }
            )


class StandBy(models.Model):
    """
    Represents a stand-by record in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        start_time (models.DateTimeField): The start time of the stand-by.
        end_time (models.DateTimeField): The end time of the stand-by.
        type (models.ForeignKey): The type of hours associated with the stand-by (HourType).
        badge_num (models.ForeignKey): The member's badge number (Member).
        losap_valid (models.BooleanField): Indicates whether the stand-by counts for LOSAP.

    Meta:
        db_table (str): The name of the database table for this model.
        verbose_name (str): The human-readable name of the model.

    Example:
        To create a new stand-by record:

        ```python
        standby = StandBy.objects.create(
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=2),
            type=hour_type_instance,
            badge_num=member_instance
        )
        ```

    Note:
        This model represents stand-by records. Stand-by records are associated with a member,
        a type of hours (e.g., "Regular" or "Overtime"), and a LOSAP validity flag.

    """

    start_time = models.DateTimeField(db_column="StartTime")
    end_time = models.DateTimeField(db_column="EndTime")
    type = models.ForeignKey(HourType, models.RESTRICT, db_column="Type")
    badge_num = models.ForeignKey(
        Member, models.CASCADE, db_column="BadgeNum", related_name="standby"
    )
    losap_valid = models.BooleanField(db_column="LOSAPValid", default=False)

    class Meta:
        """Meta data of Stand By."""

        db_table = "StandBy"
        verbose_name = "Stand By"

    def __str__(self):
        """Return a string representation of a Stand By."""
        # TODO Clean up datetime.
        return (
            f"{type(self)._meta.verbose_name}: {self.badge_num.full_name()}"
            + f" {self.start_time.strftime('%Y-%m-%d %H:%M')} -"
            + f" {self.end_time.strftime('%Y-%m-%d %H:%M')}"
        )

    def save(self, *args, **kwargs):
        """Save to check if the Stand By counts for LOSAP."""
        time_diff = self.end_time - self.start_time

        min_seconds = (self.type.min_hours * 3600) - 60
        if time_diff.total_seconds() >= min_seconds:
            self.losap_valid = True
        else:
            self.losap_valid = False

        super().save(*args, **kwargs)

    def clean(self):
        """Validate Sleep In does not overlap with other entities."""
        for sleepIn in SleepIn.objects.filter(badge_num=self.badge_num):
            sleepIn_start_time = datetime(
                sleepIn.date.year, sleepIn.date.month, sleepIn.date.day
            ).replace(hour=19, minute=0, tzinfo=pytz.timezone(settings.TIME_ZONE))
            sleepIn_end_time = datetime(
                sleepIn.date.year, sleepIn.date.month, sleepIn.date.day
            ).replace(
                hour=6, minute=59, tzinfo=pytz.timezone(settings.TIME_ZONE)
            ) + timedelta(
                days=1
            )
            if (
                (
                    self.start_time >= sleepIn_start_time
                    and self.start_time <= sleepIn_end_time
                )
                or (
                    self.end_time >= sleepIn_start_time
                    and self.end_time < sleepIn_end_time
                )
                or (
                    self.start_time <= sleepIn_end_time
                    and self.end_time >= sleepIn_start_time
                )
            ):
                raise ValidationError(
                    {
                        "message": (
                            f"{type(self)._meta.verbose_name} cannot overlap"
                            + " with a Sleep In."
                        )
                    }
                )

        if (
            StandBy.objects.filter(
                badge_num=self.badge_num,
                start_time__gte=self.start_time,
                start_time__lte=self.end_time,
            )
            .exclude(pk=self.pk)
            .count()
            or StandBy.objects.filter(
                badge_num=self.badge_num,
                end_time__gte=self.start_time,
                end_time__lt=self.end_time,
            )
            .exclude(pk=self.pk)
            .count()
            or StandBy.objects.filter(
                badge_num=self.badge_num,
                start_time__lte=self.end_time,
                end_time__gte=self.start_time,
            )
            .exclude(pk=self.pk)
            .count()
        ):
            raise ValidationError(
                {
                    "message": (
                        f"{type(self)._meta.verbose_name} cannot overlap with"
                        + " a Stand By."
                    )
                }
            )
        elif (
            CollateralDuty.objects.filter(
                badge_num=self.badge_num,
                start_time__gte=self.start_time,
                start_time__lte=self.end_time,
            ).count()
            or CollateralDuty.objects.filter(
                badge_num=self.badge_num,
                end_time__gte=self.start_time,
                end_time__lt=self.end_time,
            ).count()
            or CollateralDuty.objects.filter(
                badge_num=self.badge_num,
                start_time__lte=self.end_time,
                end_time__gte=self.start_time,
            ).count()
        ):
            raise ValidationError(
                {
                    "message": (
                        f"{type(self)._meta.verbose_name} cannot overlap with"
                        + " a Collateral Duty."
                    )
                }
            )


class TrainingReport(models.Model):
    """
    Represents a training report in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        id (models.IntegerField): The primary key of the training report.
        training_date (models.DateTimeField): The date of the training.
        sub_date (models.DateTimeField): The submission date of the training report.
        course_code (models.ForeignKey): The code of the course associated with the report (CourseCode).
        certified (models.BooleanField): Indicates whether the report is certified.
        num_hours (models.FloatField): The number of hours of training.
        description (models.CharField): A brief description of the training.

    Meta:
        db_table (str): The name of the database table for this model.
        verbose_name (str): The human-readable name of the model.

    Example:
        To create a new training report:

        ```python
        training_report = TrainingReport.objects.create(
            training_date=datetime.now(),
            sub_date=datetime.now(),
            course_code=course_code_instance,
            certified=True,
            num_hours=4.5,
            description="Fire safety training"
        )
        ```

    """

    id = models.IntegerField(primary_key=True)
    training_date = models.DateTimeField(db_column="TrainingDate")
    sub_date = models.DateTimeField(db_column="SubDate")
    course_code = models.ForeignKey(CourseCode, models.RESTRICT, db_column="CourseCode")
    certified = models.BooleanField(db_column="Certified")
    num_hours = models.FloatField(db_column="numHours")
    description = models.CharField(db_column="Description", max_length=50)

    class Meta:
        """Meta data of Training Report."""

        db_table = "TrainingReport"
        verbose_name = "Training Report"


class UnitResponse(models.Model):
    """
    Represents a unit's response to an incident in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        call_sign (models.OneToOneField): The call sign of the unit (Unit).
        incident_num (models.ForeignKey): The incident number associated with the response (Incident).
        dispatch_time (models.DateTimeField): The time of dispatch for the unit.
        cleared_time (models.DateTimeField): The time when the unit was cleared from the incident (optional).

    Meta:
        db_table (str): The name of the database table for this model.
        verbose_name (str): The human-readable name of the model.

    Example:
        To create a new unit response record:

        ```python
        unit_response = UnitResponse.objects.create(
            call_sign=unit_instance,
            incident_num=incident_instance,
            dispatch_time=datetime.now(),
            cleared_time=datetime.now() + timedelta(hours=2)
        )
        ```

    """

    call_sign = models.OneToOneField(
        "Unit", models.RESTRICT, db_column="CallSign", primary_key=True
    )
    incident_num = models.ForeignKey(
        Incident, models.CASCADE, db_column="IncidentNum", to_field="incident_num"
    )
    dispatch_time = models.DateTimeField(db_column="DispatchTime")
    cleared_time = models.DateTimeField(db_column="ClearedTime", blank=True, null=True)

    class Meta:
        """Meta data of Unit Response."""

        db_table = "UnitResponse"
        verbose_name = "Unit Response"
        models.UniqueConstraint(
            fields=["incident_num", "call_sign"], name="unique_unit_response"
        )
        ordering = ["incident_num", "call_sign"]


class Unit(models.Model):
    """
    Represents a unit in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        call_sign (models.CharField): The call sign of the unit (primary key).
        unit_type (models.CharField): The type or category of the unit.
        max_crew (models.IntegerField): The maximum number of crew members for the unit.

    Meta:
        db_table (str): The name of the database table for this model.

    Example:
        To create a new unit:

        ```python
        unit = Unit.objects.create(
            call_sign="ABC123",
            unit_type="Fire Engine",
            max_crew=4
        )
        ```

    """

    call_sign = models.CharField(db_column="CallSign", primary_key=True, max_length=6)
    unit_type = models.CharField(db_column="UnitType", max_length=10)
    max_crew = models.IntegerField(db_column="MaxCrew")

    class Meta:
        """Meta data of Unit."""

        db_table = "Unit"
