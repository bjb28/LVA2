# Third-Party Libraries
from rest_framework import filters, viewsets

from .models import Address, Member, Rank
from .serializers import AddressSerializer, MemberSerializer, RankSerializer


class AddressViewSet(viewsets.ModelViewSet):
    search_fields = ["^box_area", "^street_name"]
    filter_backends = (filters.SearchFilter,)
    queryset = Address.objects.all().order_by("box_area")
    serializer_class = AddressSerializer


class MemberViewSet(viewsets.ModelViewSet):
    search_fields = ["^badge_num", "^last_name", "^first_name"]
    filter_backends = (filters.SearchFilter,)
    queryset = Member.objects.all().order_by("last_name")
    serializer_class = MemberSerializer


class RankViewSet(viewsets.ModelViewSet):
    search_fields = ["^abbr"]
    filter_backends = (filters.SearchFilter,)
    queryset = Rank.objects.all().order_by("abbr")
    serializer_class = RankSerializer
