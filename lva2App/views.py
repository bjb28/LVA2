"""LVA2 App View.s"""
# Third-Party Libraries
from django.shortcuts import render


def home(request):
    """Return the home page."""
    return render(request, "pages/home.html", {})


def losapHoursView(request, year="", month=""):
    """Display the LOSAP Hours Report."""

    context = {"year": year, "month": month}

    return render(request, "pages/losap_hours.html", context)


def memberHourView(request, badge_number, year="", month=""):
    """Display the Member's page for hours tracking."""

    context = {"badge_num": badge_number, "year": year, "month": month}

    return render(request, "pages/member_hours.html", context)


def memberHourSearchView(request):
    """Displays a search box to get to a member's hours."""
    return render(request, "pages/member_hours_search.html", {})
