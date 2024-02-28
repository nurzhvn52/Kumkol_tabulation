from .models import *
from rest_framework import serializers

class TabelFactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fact_tabel
        fields = ("__all__")

