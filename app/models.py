from django.db import models

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    def __str__(self):
        return f"{self.id} - {self.name}"


class TrainerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    number_of_jobs = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.id} - {self.name}"

    

class Job(models.Model):
    class Status(models.TextChoices):
        ACCEPTED = 'accepted', "Accepted"
        PUBLISHED = 'published', "Published"

    class Title(models.TextChoices):
        TRAINING_SESSION = 'training_session', "Training session"
        CONSULTATIONS = 'consultations', "Consultations"

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    description = models.CharField(max_length=512)
    status = models.CharField(
            max_length=100, 
            choices=Status.choices,
            default=Status.PUBLISHED,
    )
    title = models.CharField(
            max_length=100,
            choices=Title.choices,
            default=Title.TRAINING_SESSION,
    )
    budget = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    start_time = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.name} - {self.title}"
    def delete_job(self):
        self.delete()


class Bid(models.Model):
    bidder = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    accepted = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    disputed = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.bidder.name} - {self.job.title} - {self.price}"


class Dispute(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    bid = models.OneToOneField(Bid, on_delete=models.CASCADE)
    reason = models.TextField(blank=False, null=False)


class TopUp(models.Model):
    code = models.CharField(max_length=12)
    expiration_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_used = models.BooleanField(default=False)

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    used_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} - {self.expiration_date} - {self.amount} - {self.is_used}"


