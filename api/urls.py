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
    MemberViewSet,
    RankViewSet,
    SleepInViewSet,
    StandByViewSet,
    UnitViewSet,
)

router = routers.DefaultRouter()
router.register(r"address", AddressViewSet)
router.register(r"collateral-duty", CollateralDutyViewSet)
router.register(r"committee", CommitteeViewSet)
router.register(r"course-code", CourseCodeViewSet)
router.register(r"hour-type", HourTypeViewSet)
router.register(r"member", MemberViewSet)
router.register(r"rank", RankViewSet)
router.register(r"sleep-in", SleepInViewSet)
router.register(r"stand-by", StandByViewSet)
router.register(r"unit", UnitViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
