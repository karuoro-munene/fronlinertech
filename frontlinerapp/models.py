from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
import datetime
from pinax.referrals.models import Referral
from frontlinerapi import settings


USER_TRANSACTION_TYPES = [
    ("PAY", "PAY"),
    ("RECEIVE", "RECEIVE")
]


TRANSACTION_TYPES = [
    ("DIRECT", "DIRECT"),
    ("SPILL", "SPILL"),
    ("WITHDRAWAL", "WITHDRAWAL")
]


SYSTEM_TRANSACTION_TYPES = [
    ("INITIAL", "INITIAL"),
    ("ONE", "ONE"),
    ("TWO", "TWO"),
    ("THREE", "THREE"),
    ("WITHDRAWAL", "WITHDRAWAL")
]


class CustomUser(AbstractUser):
    email = models.EmailField(null=True, blank=True)
    country = models.CharField(max_length=100,blank=True,null=True)
    phonenumber = models.CharField(max_length=100,blank=True,null=True)
    is_regularuser = models.BooleanField(default=False)
    is_adminuser = models.BooleanField(default=False)
    first_time_login = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    def last_seen(self):
        return cache.get('seen_%s' % self.username)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > self.last_seen() + datetime.timedelta(
                    seconds=settings.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    referral = models.OneToOneField(Referral, on_delete=models.CASCADE, null=True)
    one_level_up_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='one_level_up_user', null=True)
    two_levels_up_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='two_levels_up_user', null=True)
    three_levels_up_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='three_levels_up_user', null=True)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        referral = Referral.create(user=profile.user,redirect_to=reverse("home"))
        profile.referral = referral
        profile.save()


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Chat(models.Model):
    members = models.ManyToManyField(CustomUser)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now
        super(Chat, self).save(*args, **kwargs)


class Message(models.Model):
    chat = models.ForeignKey(Chat,on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    pub_date = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['pub_date']

    def __str__(self):
        return self.message


class UserWallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    total_balance = models.IntegerField(null=True)
    direct_earnings = models.IntegerField(null=True)
    spill_earnings = models.IntegerField(null=True)
    pending_spills = models.IntegerField(null=True)
    pending_cashout = models.IntegerField(null=True)
    settled_cashout = models.IntegerField(null=True)
    created_at = models.DateTimeField(default=timezone.now)


class SystemWallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    total_balance = models.IntegerField(null=True)
    level_one_earnings = models.IntegerField(null=True)
    level_two_earnings = models.IntegerField(null=True)
    level_three_earnings = models.IntegerField(null=True)
    created_at = models.DateTimeField(default=timezone.now)


class UserTransactions(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True)
    type = models.CharField(max_length=10,choices=USER_TRANSACTION_TYPES,null=True)
    from_who = models.CharField(max_length=50, null=True)
    transaction_type = models.CharField(max_length=10,choices=TRANSACTION_TYPES, null=True)
    created_at = models.DateTimeField(default=timezone.now)


class SystemTransactions(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True)
    type = models.CharField(max_length=10,choices=SYSTEM_TRANSACTION_TYPES,null=True)
    created_at = models.DateTimeField(default=timezone.now)
