from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone

class trade(models.Model):
	user_giving_skins = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='trades_skins', null=True, blank=True)
	user_giving_money = models.ForeignKey(settings.AUTH_USER_MODEL, null=True , related_name='trades_money', blank=True)
	skins_assetids = models.TextField(null=True)
	amount_submitted = models.CharField(max_length=50,null=True)
	#trade status= money submitted/trade submitted/Complete sending respective items/nothing submitted
	skins_submitted = models.CharField(max_length=10,null=True)
	#image for skins
	skins_submitted_icons = models.TextField(null=True)
	#name for skins
	skins_submitted_name = models.TextField(null=True)
	#money submitted is the amount of money submitted
	trade_reverted = models.CharField(max_length=10,null=True)
	time_posted = models.DateTimeField(auto_now_add=True, blank=True, null=True)

	money_reverted = models.CharField(max_length=10,null=True)
	money_submitted = models.CharField(max_length=10,null=True)
	random_string = models.CharField(max_length=100, unique=True) 
	created_by = models.CharField(max_length=100)
	mobileNumber = models.CharField(max_length=10, null=True)
	expectedAmount = models.CharField(max_length=10, null=True)

	def __str__(self):
		if self.user_giving_skins is None:
			string = "created by- "+ self.user_giving_money.username + ", id= " + self.random_string
			return string
		else:
			string = "created by- "+ self.user_giving_skins.username + ", id= " + self.random_string
			return string


class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	steam_id = models.CharField(max_length=50, unique=True,  null=True)
	phone_no = models.CharField(max_length=14, null=True)
	tradeUrl = models.CharField(max_length=50, unique=True,  null=True)
	isConfirmed = models.BooleanField(default=False)
	

	# running_ad = models.ForeignKey(Ad, blank=True, null=True)

	def __str__(self):
		return 'Profile for user {}'.format(self.user.username)

class Comments(models.Model):
    user = models.ForeignKey(User)
    text = models.CharField(max_length=255)

