from api.models import User
from tpong.models import PongStats, PongMatch
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class StatsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = PongStats
        fields = ['user', 'playerName', 'score', 'side']

class PongMatchSerializer(serializers.ModelSerializer):
    stats = StatsSerializer(many=True, read_only=True)
    class Meta:
        model = PongMatch
        fields = ['id', 'type', 'mode', 'stats', 'maxScore']

