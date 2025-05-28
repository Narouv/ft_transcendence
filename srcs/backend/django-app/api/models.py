from django.db import models
from django.db.models import Q
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User, AbstractUser
import datetime
import os

# Create your models here.

class User(AbstractUser):
    nickname = models.CharField(max_length=25, blank=True)
    online = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to="avatar/", default="avatar/defaultAvatar.png")

    def isOnline(self):
        return self.online != 0

    def getNick(self):
        return self.nickname if self.nickname else self.username
    
    def hasDefaultAvatar(self):
        return self.avatar == "avatar/defaultAvatar.png"
    
    def setAvatar(self, image):
        if not self.hasDefaultAvatar():
            if os.path.isfile(self.avatar.path):
                os.remove(self.avatar.path)
        self.avatar = image
        self.save()

class FriendRequest(models.Model):
    PENDING="pending"
    ACCEPTED="accepted"
    DECLINED="declined"
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined'),
    ]

    created_at = models.TimeField(auto_now=False, auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=PENDING)

    def getActiveFriends(user):
        activeRequests = FriendRequest.objects.filter(
                Q(sender=user, status='accepted') | Q(receiver=user, status='accepted')
        )
        activeFriends = User.objects.filter(
            Q(sent_friend_requests__in=activeRequests) | Q(received_friend_requests__in=activeRequests)
        ).exclude(pk=user.id).distinct()
        return activeFriends

    def getActiveUserRelation(user1, user2):
        try:
            result = FriendRequest.objects.get(
                Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1),
                status='accepted'
            )
        except:
            return False
        return result

    def getExistingUserRelation(user1, user2):
        try:
            result = FriendRequest.objects.get(
                Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1)
            )
        except:
            return False
        return result

class TwoFactor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    secret = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)