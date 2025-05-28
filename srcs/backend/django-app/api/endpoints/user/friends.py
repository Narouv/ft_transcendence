from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response 
from rest_framework.views import APIView
from rest_framework import serializers
from api.models import FriendRequest, User
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'online']

class FriendRequestSerializer(serializers.ModelSerializer):
    created_at = serializers.TimeField(format='%I:%M %p')
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    class Meta:
        model = FriendRequest
        fields = ['id', 'created_at', 'sender', 'receiver', 'status']

class FriendAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        friends = FriendRequest.getActiveFriends(request.user)
        serializer = UserSerializer(friends, many=True)
        return Response({"success": True, "data": serializer.data})
    
    def delete(self, request):
        try:
            username = request.data["username"]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"success": False, "error": "Target user not found!"})
        friendRequest = FriendRequest.getActiveUserRelation(request.user, user)
        if not friendRequest or friendRequest.status != FriendRequest.ACCEPTED:
            return Response({"success": False, "error": "Not a friend"})
        friendRequest.delete()
        return Response({"success": True})

class FriendRequestAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        pendingRequestsOut = FriendRequest.objects.filter(sender=request.user, status=FriendRequest.PENDING)
        pendingRequestsIn = FriendRequest.objects.filter(receiver=request.user, status=FriendRequest.PENDING)
        serializerOut = FriendRequestSerializer(pendingRequestsOut, many=True)
        serializerIn = FriendRequestSerializer(pendingRequestsIn, many=True)
        return Response({
            "success": True, 
            "data": { "in": serializerIn.data, "out": serializerOut.data },
            
        })        

    def post(self, request):
        try:
            username = request.data["username"]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            target = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"success": False, "error": "Target user not found!"})
        if request.user == target:
            return Response({"success": False, "error": "Cant send to yourself"})
        if FriendRequest.getExistingUserRelation(request.user, target):
            return Response({"success": False, "error": "Already sent"})
        friendRequest = FriendRequest(sender=request.user, receiver=target)
        friendRequest.save()
        return Response({ "success": True })

    def patch(self, request):
        try:
            id = request.data["id"]
            action = request.data["action"]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            friendRequest = FriendRequest.objects.get(pk=id, status=FriendRequest.PENDING)
        except FriendRequest.DoesNotExist:
            return Response({"success": False, "error": "Request id invalid / not pending"})
        if request.user.id != friendRequest.receiver.id:
            return Response({"success": False, "error": "Not authorized"})
        if action == "accept":
            friendRequest.status = FriendRequest.ACCEPTED
            friendRequest.save()
        elif action == "decline":
            friendRequest.delete()
        else:
            return Response({"success": False, "error": "Invalid action"})
        return Response({"success": True})
    
    def delete(self, request):
        try:
            id = request.data["id"]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            friendRequest = FriendRequest.objects.get(pk=id)
        except FriendRequest.DoesNotExist:
            return Response({"success": False, "error": "Request id invalid"})
        if request.user != friendRequest.sender and request.user != friendRequest.receiver:
            return Response({"success": False, "error": "Not authorized"})
        if friendRequest.status != FriendRequest.PENDING:
            return Response({"success": False, "error": "Request not pending"})
        friendRequest.delete()
        return Response({"success": True})

