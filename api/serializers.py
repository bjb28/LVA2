# Third-Party Libraries
from rest_framework import serializers

from .models import Address, Member, Rank


class AddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Address
        fields = ("street_num", "street_name", "box_area", "apt_num")


class MemberSerializer(serializers.HyperlinkedModelSerializer):
    rank = serializers.PrimaryKeyRelatedField(queryset=Rank.objects.all())

    class Meta:
        model = Member
        fields = ("badge_num", "last_name", "first_name", "rank", "created", "updated")


class RankSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Rank
        fields = ("abbr", "is_officer", "name")
