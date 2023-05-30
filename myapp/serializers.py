from rest_framework import serializers
from .models import DailyStats

class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStats
        fields = '__all__'