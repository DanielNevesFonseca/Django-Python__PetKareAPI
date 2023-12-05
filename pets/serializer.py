from rest_framework import serializers
from .models import Sex
from groups.serializer import GroupSerializer
from traits.serializer import TraitSerializer


class PetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50, required=True)
    age = serializers.IntegerField(required=True)
    weight = serializers.FloatField(required=True)
    sex = serializers.ChoiceField(choices=Sex.choices, required=False)

    group = GroupSerializer(required=True)
    traits = TraitSerializer(many=True, required=True)
