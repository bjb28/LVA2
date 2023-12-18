"""API URLs."""
# Third-Party Libraries
from django.urls import include, path
from rest_framework import routers

from .views import (
    AddressViewSet,
    CollateralDutyViewSet,
    CommitteeViewSet,
    CourseCodeViewSet,
    HourTypeViewSet,
    LosapHoursViewSet,
    MemberViewSet,
    RankViewSet,
    SleepInViewSet,
    StandByViewSet,
    TrainingReportViewSet,
    UnitViewSet,
)

router = routers.DefaultRouter()
router.register(r"address", AddressViewSet)
router.register(r"collateral-duty", CollateralDutyViewSet)
router.register(r"committee", CommitteeViewSet)
router.register(r"course-code", CourseCodeViewSet)
router.register(r"hour-type", HourTypeViewSet)
router.register(r"losap-hours", LosapHoursViewSet, basename="losap_hours")
router.register(r"member", MemberViewSet)
router.register(r"rank", RankViewSet)
router.register(r"sleep-in", SleepInViewSet)
router.register(r"stand-by", StandByViewSet)
router.register(r"training-report", TrainingReportViewSet)
router.register(r"unit", UnitViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "api/losap-hours/<int:year>/",
        LosapHoursViewSet.as_view({"get": "list"}),
        name="losap-hours-year",
    ),
    path(
        "api/losap-hours/<int:year>/<int:month>/",
        LosapHoursViewSet.as_view({"get": "list"}),
        name="losap-hours-month",
    ),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
