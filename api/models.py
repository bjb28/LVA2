# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
# Third-Party Libraries
from django.db import models


class Addresses(models.Model):
    """
    Represents an address in the database.

    Args:
        models.Model: The base class for all Django models.

    Attributes:
        streetNum (models.IntegerField): The street number of the address.
        streetName (models.CharField): The name of the street.
        boxArea (models.CharField): The box or area associated with the address.
        aptNum (models.CharField): The apartment number (optional).

    Meta:
        managed (bool): Indicates whether this model is managed by Django's database
            migrations.
        db_table (str): The name of the database table for this model.
        models.UniqueConstraint: Ensures the uniqueness of the combination of streetNum,
            streetName, and aptNum.
        ordering (list of str): The default ordering for querysets of this model, first
            ordered by 'boxArea' and then by 'streetName'.

    Example:
        To create a new address:

        ```
        address = Addresses.objects.create(
            streetNum=123,
            streetName="Main St",
            boxArea="Box A",
            aptNum="Apt 101"
        )
        ```

    Note:
        This model is set as unmanaged (`managed = False`), meaning that Django won't
        create a database table for it automatically.
    """

    street_num = models.IntegerField(db_column="StreetNum")
    street_name = models.CharField(db_column="StreetName", max_length=100)
    box_area = models.CharField(db_column="BoxArea", max_length=10)
    apt_num = models.CharField(db_column="AptNum", max_length=20, blank=True, null=True)

    class Meta:
        db_table = "Addresses"
        models.UniqueConstraint(
            fields=["street_num", "street_name", "apt_num"], name="unique_address"
        )
        ordering = ["box_area", "street_name"]


class CollateralDuty(models.Model):
    start_time = models.DateTimeField(db_column="StartTime")
    end_time = models.DateTimeField(db_column="EndTime")
    type = models.ForeignKey("HourTypes", on_delete=models.RESTRICT, db_column="Type")
    committee = models.ForeignKey(
        "Committees", on_delete=models.RESTRICT, db_column="Committee"
    )
    description = models.CharField(db_column="Description", max_length=120)
    badge_num = models.ForeignKey(
        "Members", on_delete=models.CASCADE, db_column="BadgeNum"
    )

    class Meta:
        db_table = "CollateralDuty"
        verbose_name = "Collateral Duty"

    def __str__(self):
        return (
            f"{type(self)._meta.verbose_name}: {self.badge_num.full_name()}"
            + f" {self.start_time.strftime('%Y-%m-%d %H:%M')} -"
            + f" {self.end_time.strftime('%Y-%m-%d %H:%M')}"
        )


class Committees(models.Model):
    name = models.CharField(db_column="Name", primary_key=True, max_length=50)

    class Meta:
        db_table = "Committees"


class CourseCodes(models.Model):
    code = models.CharField(db_column="Code", primary_key=True, max_length=6)
    name = models.CharField(db_column="Name", max_length=50)

    class Meta:
        db_table = "CourseCodes"


class HourTypes(models.Model):
    name = models.CharField(db_column="Name", primary_key=True, max_length=20)
    min_hours = models.IntegerField(db_column="MinHours", blank=True, null=True)

    class Meta:
        db_table = "HourTypes"


class Incidents(models.Model):
    incident_num = models.IntegerField(db_column="IncidentNum", primary_key=True)
    address = models.ForeignKey(Addresses, models.RESTRICT, db_column="Address")
    incidentType = models.CharField(
        db_column="IncidentType", max_length=10, blank=True, null=True
    )
    officer = models.IntegerField(db_column="Officer", blank=True, null=True)
    dispatch_time = models.DateTimeField(db_column="DispatchTime")
    cleared_time = models.DateTimeField(db_column="ClearedTime", blank=True, null=True)
    created_time = models.DateTimeField(db_column="CreatedTime", blank=True, null=True)
    updated_time = models.DateTimeField(db_column="UpdatedTime", blank=True, null=True)

    class Meta:
        db_table = "Incidents"


class MemberResponse(models.Model):
    badge_num = models.OneToOneField(
        "Members", models.CASCADE, db_column="BadgeNum", primary_key=True
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
        db_table = "MemberResponse"
        models.UniqueConstraint(
            fields=["unit__incident_num", "unit__call_sign", "badge_num"], name="unique_mbr_response"
        )
        ordering = ["unit__incident_num", "unit__call_sign", "badge_num"]


class MemberTrainingReport(models.Model):
    badge_num = models.OneToOneField(
        "Members", models.CASCADE, db_column="BadgeNum", primary_key=True
    )
    training_report = models.ForeignKey(
        "TrainingReport", models.CASCADE, db_column="TrainingReport"
    )

    class Meta:
        db_table = "MemberTrainingReport"
        models.UniqueConstraint(
            fields=["training_report", "badge_num"], name="unique_training_report"
        )
        ordering = ["training_report", "badge_num"]


class Members(models.Model):
    badge_num = models.IntegerField(db_column="BadgeNum", primary_key=True)
    first_name = models.CharField(db_column="FirstName", max_length=50)
    last_name = models.CharField(db_column="LastName", max_length=50)
    rank = models.ForeignKey("Ranks", models.RESTRICT, db_column="Rank")

    class Meta:
        db_table = "Members"
        models.UniqueConstraint(
            fields=["badge_num", "first_name", "last_name"], name="unique_member"
        )

    def full_name(self):
        """Returns a string of the last name, first name of the member."""
        return f"{self.last_name}, {self.first_name}"

    def full_member(self):
        """Returns a string of the last name, first name(badge number)."""
        return f"{self.last_name}, {self.first_name}({self.badge_num})"


class Ranks(models.Model):
    abbr = models.CharField(db_column="Abbr", primary_key=True, max_length=10)
    is_officer = models.IntegerField(db_column="IsOfficer")
    name = models.CharField(db_column="Name", max_length=100)

    class Meta:
        db_table = "Ranks"


class SleepIn(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateTimeField(db_column="Date")
    type = models.ForeignKey(HourTypes, models.RESTRICT, db_column="Type")
    badge_num = models.ForeignKey(Members, models.CASCADE, db_column="BadgeNum")

    class Meta:
        db_table = "SleepIn"
        verbose_name = "Sleep In"

    def __str__(self):
        return f"""{type(self)._meta.verbose_name} {self.badge_num.full_name()} \
            {self.date}"""


class Standby(models.Model):
    id = models.IntegerField(primary_key=True)
    start_time = models.DateTimeField(db_column="StartTime")
    end_time = models.DateTimeField(db_column="EndTime")
    type = models.ForeignKey(HourTypes, models.RESTRICT, db_column="Type")
    badge_num = models.ForeignKey(Members, models.CASCADE, db_column="BadgeNum")

    class Meta:
        db_table = "StandBy"
        verbose_name = "Stand By"

    def __str__(self):
        # TODO Clean up datetime.
        return (
            f"{type(self)._meta.verbose_name}: {self.badge_num.full_name()}"
            + f" {self.start_time.strftime('%Y-%m-%d %H:%M')} -"
            + f" {self.end_time.strftime('%Y-%m-%d %H:%M')}"
        )


class TrainingReport(models.Model):
    id = models.IntegerField(primary_key=True)
    training_date = models.DateTimeField(db_column="TrainingDate")
    sub_date = models.DateTimeField(db_column="SubDate")
    course_code = models.ForeignKey(
        CourseCodes, models.RESTRICT, db_column="CourseCode"
    )
    certified = models.BooleanField(db_column="Certified")
    num_hours = models.FloatField(db_column="numHours")
    description = models.CharField(db_column="Description", max_length=50)

    class Meta:
        db_table = "TrainingReport"
        verbose_name = "Training Report"


class UnitResponse(models.Model):
    call_sign = models.OneToOneField(
        "Units", models.RESTRICT, db_column="CallSign", primary_key=True
    )
    incident_num = models.ForeignKey(
        Incidents, models.CASCADE, db_column="IncidentNum", to_field="incident_num"
    )
    dispatch_time = models.DateTimeField(db_column="DispatchTime")
    cleared_time = models.DateTimeField(db_column="ClearedTime", blank=True, null=True)

    class Meta:
        db_table = "UnitResponse"
        verbose_name = "Unit Response"
        models.UniqueConstraint(
            fields=["incident_num", "call_sign"], name="unique_unit_response"
        )
        ordering = ["incident_num", "call_sign"]


class Units(models.Model):
    call_sign = models.CharField(db_column="CallSign", primary_key=True, max_length=6)
    unit_type = models.CharField(db_column="UnitType", max_length=10)
    max_crew = models.IntegerField(db_column="MaxCrew")

    class Meta:
        db_table = "Units"
