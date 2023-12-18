"""API Views."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework import filters, status, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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
    TrainingReport,
    Unit,
)
from .serializers import (
    AddressSerializer,
    CollateralDutySerializer,
    CombinedHoursSerializer,
    CommitteeSerializer,
    CourseCodeSerializer,
    HourTypeSerializer,
    MemberSerializer,
    RankSerializer,
    SleepInSerializer,
    StandBySerializer,
    TrainingReportSerializer,
    UnitSerializer,
)


class AddressViewSet(viewsets.ModelViewSet):
    """View Set for Address."""

    search_fields = ["^box_area", "^street_name"]
    filter_backends = (filters.SearchFilter,)
    queryset = Address.objects.all().order_by("box_area")
    serializer_class = AddressSerializer


class CollateralDutyViewSet(viewsets.ModelViewSet):
    """View Set for Collateral Duty."""

    search_fields = ["^start_time", "^badge_num", "^committee"]
    filter_backends = (filters.SearchFilter,)
    queryset = CollateralDuty.objects.all().order_by("start_time")
    serializer_class = CollateralDutySerializer

    def get_queryset(self):
        """Allow for searching by year, month, and badge num.

        Example:
        /?month=&year=&badge_num=54321
        """
        queryset = CollateralDuty.objects.all().order_by("start_time")
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")
        badge_num = self.request.query_params.get("badge_num")

        # Filter by month and year if provided
        if month and year:
            queryset = queryset.filter(start_time__month=month, start_time__year=year)
        elif year:
            queryset = queryset.filter(start_time__year=year)

        # Filter by badge_num if provided
        if badge_num:
            queryset = queryset.filter(badge_num=badge_num)

        return queryset


class CommitteeViewSet(viewsets.ModelViewSet):
    """View Set for Committee."""

    search_fields = ["^name"]
    filter_backends = [
        filters.SearchFilter,
    ]
    queryset = Committee.objects.all().order_by("name")
    serializer_class = CommitteeSerializer


class CourseCodeViewSet(viewsets.ModelViewSet):
    """View Set for Course Code."""

    search_fields = ["^code", "^name"]
    filter_backends = [
        filters.SearchFilter,
    ]
    queryset = CourseCode.objects.all().order_by("code")
    serializer_class = CourseCodeSerializer


class HourTypeViewSet(viewsets.ModelViewSet):
    """View Set for Hour Type."""

    search_fields = ["^name"]
    filter_backends = [
        filters.SearchFilter,
    ]
    queryset = HourType.objects.all().order_by("name")
    serializer_class = HourTypeSerializer


class LosapHoursViewSet(viewsets.ViewSet):
    """View Set for returning all Losap Hours."""

    def list(self, requests, year="", month=""):
        """Return all members hours.

        Call with: /api/losap_hours/?month=<>&year=<>
        """
        timezone.activate(settings.TIME_ZONE)

        # Holds all the members' hours
        members_hours = list()

        for member in Member.objects.all():
            # Define base query
            query_standby = Q(badge_num=member.badge_num)
            query_collateralduty = Q(badge_num=member.badge_num)
            query_sleepin = Q(badge_num=member.badge_num)

            # Apply filters for month and year if provided
            if month and year:
                first_day = timezone.make_aware(datetime(int(year), int(month), 1))
                last_day = first_day + relativedelta(months=1, days=-1)

                standby_hours = StandBy.objects.filter(
                    query_standby,
                    start_time__range=(first_day, last_day),
                    losap_valid=True,
                ).count()
                collateralduty_hours = CollateralDuty.objects.filter(
                    query_collateralduty,
                    start_time__range=(first_day, last_day),
                    losap_valid=True,
                ).count()
                sleepin_hours = SleepIn.objects.filter(
                    query_sleepin, date__range=(first_day, last_day)
                ).count()
            elif year:
                first_day = timezone.make_aware(datetime(int(year), 1, 1))
                last_day = first_day + relativedelta(years=1, days=-1)

                standby_hours = StandBy.objects.filter(
                    query_standby,
                    start_time__range=(first_day, last_day),
                    losap_valid=True,
                ).count()
                collateralduty_hours = CollateralDuty.objects.filter(
                    query_collateralduty,
                    start_time__range=(first_day, last_day),
                    losap_valid=True,
                ).count()
                sleepin_hours = SleepIn.objects.filter(
                    query_sleepin, date__range=(first_day, last_day)
                ).count()
            else:
                standby_hours = StandBy.objects.filter(
                    query_standby, losap_valid=True
                ).count()
                collateralduty_hours = CollateralDuty.objects.filter(
                    query_collateralduty,
                    losap_valid=True,
                ).count()
                sleepin_hours = SleepIn.objects.filter(query_sleepin).count()

            members_hours.append(
                {
                    "member": member.badge_num,
                    "collateralduty": collateralduty_hours,
                    "sleepin": sleepin_hours,
                    "standby": standby_hours,
                }
            )

        response_data = {"members_hours": members_hours}

        return Response(response_data, status=status.HTTP_200_OK)


class MemberViewSet(viewsets.ModelViewSet):
    """View Set for Member."""

    search_fields = ["^badge_num", "^last_name", "^first_name"]
    filter_backends = (filters.SearchFilter,)
    queryset = Member.objects.all().order_by("last_name")
    serializer_class = MemberSerializer

    @action(detail=True, methods=["get"])
    def get_hours(self, request, pk=None):
        """Return a list of a members hours.

        Call with: /api/members/<badge_num>/get_hours/?month=<>&year=<>
        """
        timezone.activate(settings.TIME_ZONE)

        try:
            member = Member.objects.get(pk=pk)
            month = request.query_params.get("month")
            year = request.query_params.get("year")

            # If month and year are not provided, use the current month and year
            if not month and not year:
                current_datetime = timezone.now()
                month = current_datetime.strftime("%m")
                year = current_datetime.strftime("%Y")

        except Member.DoesNotExist:
            return Response(
                {"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Define base query
        queryStandby = Q(badge_num=member.badge_num)
        queryCollateralduty = Q(badge_num=member.badge_num)
        querySleepin = Q(badge_num=member.badge_num)

        # Apply filters for month and year if provided
        if month and year:
            first_day = timezone.make_aware(datetime(int(year), int(month), 1))
            last_day = first_day + relativedelta(months=1, days=-1)

        elif year:
            first_day = timezone.make_aware(datetime(int(year), 1, 1))
            last_day = first_day + relativedelta(years=1, days=-1)

        # Use reverse relationships to get related hours
        standby_hours = StandBy.objects.filter(
            queryStandby, start_time__range=(first_day, last_day)
        )
        collateralduty_hours = CollateralDuty.objects.filter(
            queryCollateralduty, start_time__range=(first_day, last_day)
        )
        sleepin_hours = SleepIn.objects.filter(
            querySleepin, date__range=(first_day, last_day)
        )

        # Combine all hours into a single list
        all_hours = (
            list(standby_hours) + list(collateralduty_hours) + list(sleepin_hours)
        )

        # Sort the combined list based on the type-specific fields (start_time or date)
        sorted_hours = sorted(
            all_hours,
            key=lambda x: (x.start_time if hasattr(x, "start_time") else x.date),
        )

        # Serialize the sorted hours
        serializer = CombinedHoursSerializer(sorted_hours, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RankViewSet(viewsets.ModelViewSet):
    """View Set for Rank."""

    search_fields = ["^abbr"]
    filter_backends = (filters.SearchFilter,)
    queryset = Rank.objects.all().order_by("abbr")
    serializer_class = RankSerializer


class SleepInViewSet(viewsets.ModelViewSet):
    """View Set for Sleep In."""

    search_fields = ["^date", "^badge_num"]
    filter_backends = (filters.SearchFilter,)
    queryset = SleepIn.objects.all().order_by("date")
    serializer_class = SleepInSerializer

    def get_queryset(self):
        """Allow for searching by year, month, and badge num.

        Example:
        /?month=&year=&badge_num=54321
        """
        queryset = SleepIn.objects.all().order_by("date")
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")
        badge_num = self.request.query_params.get("badge_num")

        # Filter by month and year if provided
        if month and year:
            queryset = queryset.filter(date__month=month, date__year=year)
        elif year:
            queryset = queryset.filter(date__year=year)

        # Filter by badge_num if provided
        if badge_num:
            queryset = queryset.filter(badge_num=badge_num)

        return queryset


class StandByViewSet(viewsets.ModelViewSet):
    """View Set for Stand By."""

    search_fields = [
        "^start_time",
        "^badge_num",
    ]
    filter_backends = (filters.SearchFilter,)
    queryset = StandBy.objects.all().order_by("start_time")
    serializer_class = StandBySerializer

    def get_queryset(self):
        """Allow for searching by year, month, and badge num.

        Example:
        /?month=&year=&badge_num=54321
        """
        queryset = StandBy.objects.all().order_by("start_time")
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")
        badge_num = self.request.query_params.get("badge_num")

        # Filter by month and year if provided
        if month and year:
            queryset = queryset.filter(start_time__month=month, start_time__year=year)
        elif year:
            queryset = queryset.filter(start_time__year=year)

        # Filter by badge_num if provided
        if badge_num:
            queryset = queryset.filter(badge_num=badge_num)

        return queryset


class TrainingReportViewSet(viewsets.ModelViewSet):
    """View set for Training Report."""

    search_fields = [
        "^training_date",
        "^course_code",
        "^certified",
        "^sub_date",
    ]
    filter_backends = (filters.SearchFilter,)
    queryset = TrainingReport.objects.all().order_by("sub_date")
    serializer_class = TrainingReportSerializer

    def get_queryset(self):
        """Allow for searching by year, and month, for the submission date or training date.

        Example:
        /?date_type=&month=&year=
        """
        queryset = TrainingReport.objects.all()

        date_type = self.request.query_params.get("date_type")
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")

        # Check if date_type is provided and valid
        if date_type:
            if date_type not in ["submission", "training"]:
                return self.invalid_request("Invalid date_type")

            # Apply ordering based on date_type
            queryset = queryset.order_by("sub_date" if date_type == "submission" else "training_data")
        elif month or year:
            return self.invalid_request("date_type is required when month and/or year is provided")

        # Filter by month and year if provided
        if month and year:
            queryset = queryset.filter(start_time__month=month, start_time__year=year)
        elif year:
            queryset = queryset.filter(start_time__year=year)

        # Filter by other search criteria if needed (e.g., course_code, certified)
        # Note: You can add additional filtering here based on your requirements.

        return queryset


class UnitViewSet(viewsets.ModelViewSet):
    """View Set for Unit."""

    search_fields = ["^call_sign"]
    filter_backends = [
        filters.SearchFilter,
    ]
    queryset = Unit.objects.all().order_by("call_sign")
    serializer_class = UnitSerializer
