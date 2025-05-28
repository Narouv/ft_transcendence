from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response 
from rest_framework.views import APIView
from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)

class AvatarAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]
    parser_classes = [FileUploadParser]
    byteNum8KB = 8192

    def put(self, request, format=None):
        try:
            file = request.data["file"]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        logger.warning(file.content_type)
        if file.content_type.split('/')[0] != "image":
            return Response({"success": False, "error": "File is not a image!"})
        if file.size > AvatarAPI.byteNum8KB:
            return Response({"success": False, "error": "Image is too big - max 8kb"})
        request.user.setAvatar(file)
        return Response({"success": True})
