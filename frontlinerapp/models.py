from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
import datetime
from pinax.referrals.models import Referral
from frontlinerapi import settings
import uuid


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


class User(models.Model):
    username = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return self.username


class CustomUser(AbstractUser):
    email = models.EmailField(null=True, blank=True)
    country = models.CharField(max_length=100)
    program = models.CharField(max_length=100)
    phonenumber = models.CharField(max_length=100,blank=True,null=True)
    is_regularuser = models.BooleanField(default=False)
    is_adminuser = models.BooleanField(default=False)
    first_time_login = models.BooleanField(default=True)
    paid_for_signup = models.BooleanField(default=False)

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
    one_level_up_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='one_level_up_user', null=True)
    two_levels_up_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='two_levels_up_user', null=True)
    three_levels_up_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='three_levels_up_user', null=True)
    tree_quota = models.IntegerField(null=True)


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
    initial_level_earnings = models.IntegerField(null=True)
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


class UserReferees(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    level1 = ArrayField( models.CharField(max_length=50, blank=True), null=True)
    level2 = ArrayField( models.CharField(max_length=50, blank=True), null=True)
    level3 = ArrayField( models.CharField(max_length=50, blank=True), null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


@receiver(post_save, sender=CustomUser)
def create_user_referees(sender, instance, created, **kwargs):
    if created:
        referees = UserReferees.objects.create(user=instance)
        referees.save()


class Coins(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(CustomUser, blank=True, on_delete=models.CASCADE, null=True)
    user_coins = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.uuid


class CoinRequests(models.Model):
    user = models.ForeignKey(CustomUser, blank=True, on_delete=models.CASCADE, null=True)
    coin_amount = models.IntegerField(null=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user


class CoinOffers(models.Model):
    user = models.ForeignKey(CustomUser, blank=True, on_delete=models.CASCADE, null=True)
    coin_amount = models.IntegerField(null=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user


