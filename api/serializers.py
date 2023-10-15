"""API Serializers."""
# Third-Party Libraries
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import (
    Address,
    CollateralDuty,
    Committee,
    CourseCode,
    HourType,
    Member,
    Rank,
    SleepIn,
    StandBy,
    Unit,
)


class AddressSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Address."""

    class Meta:
        """Meta class for Address Serializer."""

        model = Address
        fields = ("street_num", "street_name", "box_area", "apt_num")


class CollateralDutySerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Collateral Duty."""

    type = serializers.PrimaryKeyRelatedField(queryset=HourType.objects.all())
    committee = serializers.PrimaryKeyRelatedField(queryset=Committee.objects.all())
    badge_num = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all().order_by("badge_num")
    )

    class Meta:
        """Meta class for Collateral Duty Serializer."""

        model = CollateralDuty
        fields = [
            "id",
            "start_time",
            "end_time",
            "type",
            "committee",
            "description",
            "badge_num",
            "losap_valid",
        ]

    def create(self, validated_data):
        """Override Create to ensure Models clean is run."""
        try:
            instance = CollateralDuty(**validated_data)
            instance.clean()
            instance.save()

            return instance

        except ValidationError as e:
            raise e

    def update(self, instance, validated_data):
        """Override Update to ensure Models clean is run."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.clean()
        instance.save()
        return instance


class CommitteeSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Committee."""

    class Meta:
        """Meta class for Committee Serializer."""

        model = Committee
        fields = ("name",)


class CourseCodeSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Course Code."""

    class Meta:
        """Meta class for Course Code Serializer."""

        model = CourseCode
        fields = ("code", "name")


class HourTypeSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Hour Type."""

    class Meta:
        """Meta class for Hour Type Serializer."""

        model = HourType
        fields = ("name", "min_hours")


class MemberSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Member."""

    rank = serializers.PrimaryKeyRelatedField(queryset=Rank.objects.all())

    class Meta:
        """Meta class for Member Serializer."""

        model = Member
        fields = ("badge_num", "last_name", "first_name", "rank", "created", "updated")


class RankSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Rank."""

    class Meta:
        """Meta class for Rank Serializer."""

        model = Rank
        fields = ("abbr", "is_officer", "name")


class SleepInSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Sleep In."""

    type = serializers.PrimaryKeyRelatedField(queryset=HourType.objects.all())
    badge_num = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all().order_by("badge_num")
    )

    class Meta:
        """Meta class for Sleep In Serializer."""

        model = SleepIn
        fields = ["id", "date", "type", "badge_num"]

    def create(self, validated_data):
        """Override Create to ensure Models clean is run."""
        try:
            instance = SleepIn(**validated_data)
            instance.clean()
            instance.save()

            return instance

        except ValidationError as e:
            raise e

    def update(self, instance, validated_data):
        """Override Update to ensure Models clean is run."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.clean()
        instance.save()
        return instance


class StandBySerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Stand By."""

    type = serializers.PrimaryKeyRelatedField(queryset=HourType.objects.all())
    badge_num = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all().order_by("badge_num")
    )

    class Meta:
        """Meta class for Stand By Serializer."""

        model = StandBy
        fields = ["id", "start_time", "end_time", "type", "badge_num", "losap_valid"]

    def create(self, validated_data):
        """Override Create to ensure Models clean is run."""
        try:
            instance = StandBy(**validated_data)
            instance.clean()
            instance.save()

            return instance

        except ValidationError as e:
            raise e

    def update(self, instance, validated_data):
        """Override Update to ensure Models clean is run."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.clean()
        instance.save()
        return instance


class UnitSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Unit."""

    class Meta:
        """Meta class for Unit Serializer."""

        model = Unit
        fields = ("call_sign", "unit_type", "max_crew")


class CombinedHoursSerializer(serializers.Serializer):
    """Serializer to return all of a members hours."""

    # Fields from StandBy model
    id_standby = serializers.IntegerField(source="id", read_only=True)
    start_time_standby = serializers.DateTimeField(source="start_time", read_only=True)
    end_time_standby = serializers.DateTimeField(source="end_time", read_only=True)
    badge_num_standby = serializers.PrimaryKeyRelatedField(
        source="badge_num", queryset=Member.objects.all()
    )
    losap_valid_standby = serializers.BooleanField(source="losap_valid", read_only=True)

    # Fields from CollateralDuty model
    id_collateralduty = serializers.IntegerField(source="id", read_only=True)
    start_time_collateralduty = serializers.DateTimeField(
        source="start_time", read_only=True
    )
    end_time_collateralduty = serializers.DateTimeField(
        source="end_time", read_only=True
    )
    committee_collateralduty = serializers.PrimaryKeyRelatedField(
        source="committee", queryset=Committee.objects.all()
    )
    description_collateralduty = serializers.CharField(
        source="description", read_only=True
    )
    badge_num_collateralduty = serializers.PrimaryKeyRelatedField(
        source="badge_num", queryset=Member.objects.all()
    )
    losap_valid_collateralduty = serializers.BooleanField(
        source="losap_valid", read_only=True
    )

    # Fields from SleepIn model
    id_sleepin = serializers.IntegerField(source="id", read_only=True)
    date_sleepin = serializers.DateTimeField(source="date", read_only=True)
    badge_num_sleepin = serializers.PrimaryKeyRelatedField(
        source="badge_num", queryset=Member.objects.all()
    )

    def to_representation(self, instance):
        """Convert an instance of hour models into a dictionary for representation."""
        if isinstance(instance, StandBy):
            return {
                "id_standby": instance.id,
                "start_time_standby": instance.start_time,
                "end_time_standby": instance.end_time,
                "type_standby": instance.type.name,
                "badge_num_standby": instance.badge_num.badge_num,
                "losap_valid_standby": instance.losap_valid,
            }
        elif isinstance(instance, CollateralDuty):
            return {
                "id_collateralduty": instance.id,
                "start_time_collateralduty": instance.start_time,
                "end_time_collateralduty": instance.end_time,
                "type_collateralduty": instance.type.name,
                "committee_collateralduty": instance.committee.name,
                "description_collateralduty": instance.description,
                "badge_num_collateralduty": instance.badge_num.badge_num,
                "losap_valid_collateralduty": instance.losap_valid,
            }
        elif isinstance(instance, SleepIn):
            return {
                "id_sleepin": instance.id,
                "date_sleepin": instance.date,
                "type_sleepin": instance.type.name,
                "badge_num_sleepin": instance.badge_num.badge_num,
            }
        else:
            raise Exception("Unsupported instance type")
