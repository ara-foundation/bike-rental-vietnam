from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from tours.models import Tour


class TourSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        fields = "__all__"
        model = Tour
        read_only_fields = ["author"]
