from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver



# Create your models here.


class Mobile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Mobile_Number = models.CharField(max_length=15,default=0)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    @receiver(post_save, sender=User)
    def create_user_mobile(sender, instance, created, **kwargs):
        if created:
            Mobile.objects.create(user=instance)

class Packages(models.Model):
    Picture = models.ImageField(
        null=True, blank=True,
        height_field="height_field",
        width_field="width_field")
    height_field = models.IntegerField(default=None, blank=True, null=True)
    width_field = models.IntegerField(default=None, blank=True, null=True)
    location = models.CharField(max_length=20)
    Price = models.IntegerField()
    Description = models.TextField()

    def __str__(self):
        return self.location

class Bookings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(Packages, on_delete=models.CASCADE)
    is_Paid = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username