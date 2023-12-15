from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # email = models.EmailField(unique=True)
    ...

class FriendRequest(models.Model):

    class Meta:
        unique_together = ['from_user', 'to_user']
        
    REQUEST_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]

    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    request_status = models.CharField(max_length=10, choices=REQUEST_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user} to {self.to_user} - 'Request status' {self.request_status}"

