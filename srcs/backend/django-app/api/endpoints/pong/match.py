from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response 
from rest_framework.views import APIView
from tpong.models import PongMatch
from tpong.serializers import PongMatchSerializer
import logging

logger = logging.getLogger(__name__)

class PongMatchApi(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        id = request.data.get("id")
        if not id:
            id = request.query_params.get("id")
        if id:
            match =  PongMatch.objects.filter(pk=id, stats__user=request.user).distinct()
            if not match.count():
                return Response({"success": False, "error": "Match does not exist"})
            return Response({"success": True, 'data': PongMatchSerializer(match[0]).data})
        matches = PongMatch.objects.filter(stats__user=request.user).distinct()
        return Response({"success": True, 'data': PongMatchSerializer(matches, many=True).data})
