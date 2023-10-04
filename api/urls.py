# Third-Party Libraries
from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"address", views.AddressViewSet)
router.register(r"member", views.MemberViewSet)
router.register(r"rank", views.RankViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
