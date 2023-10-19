"""LVA2App Urls"""


# Third-Party Libraries
from django.urls import path

# Custom Libraries
from lva2App import views

urlpatterns = [
    path("", views.home, name="home"),
    path("losap-hours", views.losapHoursView, name="losap_hours"),
    path("losap-hours/<int:year>/", views.losapHoursView, name="losap_hours_year"),
    path(
        "losap-hours/<int:year>/<int:month>",
        views.losapHoursView,
        name="losap_hours_month",
    ),
    path("member-hour", views.memberHourSearchView, name="member_hour_search"),
    path("member-hour/<int:badge_number>", views.memberHourView, name="member_hour"),
    path(
        "member-hour/<int:badge_number>/<int:year>/<int:month>",
        views.memberHourView,
        name="member_hour_month",
    ),
]
