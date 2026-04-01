from django.db import models
from account.models import CustomUser

# Create your models here.
class Voter(models.Model):
    STATUS_CHOICES = (('active', 'Active'), ('inactive', 'Inactive'))
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=11, unique=True)
    otp = models.CharField(max_length=10, null=True)
    verified = models.BooleanField(default=False)
    voted = models.BooleanField(default=False)
    face_photo = models.ImageField(upload_to="faces/", null=True, blank=True)
    otp_sent = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name


class Election(models.Model):
    title = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Position(models.Model):
    name = models.CharField(max_length=50, unique=True)
    max_vote = models.IntegerField(default=1)
    priority = models.IntegerField()
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Candidate(models.Model):
    fullname = models.CharField(max_length=50)
    party = models.CharField(max_length=50, null=True, blank=True)
    photo = models.ImageField(upload_to="candidates")
    bio = models.TextField()
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    def __str__(self):
        return self.fullname


class Votes(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)