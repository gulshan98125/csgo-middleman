from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone

class trade(models.Model):
	user_giving_skins = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='trades_skins', null=True, blank=True)
	user_giving_money = models.ForeignKey(settings.AUTH_USER_MODEL, null=True , related_name='trades_money', blank=True)
	trade_status = models.CharField(max_length=100)
	random_string = models.CharField(max_length=100, unique=True) 
	created_by = models.CharField(max_length=100)

	def __str__(self):
		return self.user_giving_skins + self.user_giving_money

class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	steam_id = models.CharField(max_length=50, unique=True,  null=True)
	phone_no = models.CharField(max_length=14, null=True)
	

	# running_ad = models.ForeignKey(Ad, blank=True, null=True)

	def __str__(self):
		return 'Profile for user {}'.format(self.user.username)

class Comments(models.Model):
    user = models.ForeignKey(User)
    text = models.CharField(max_length=255)

