# encoding: utf-8

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from oauth2client.contrib.django_util.models import CredentialsField

class UserProfile(models.Model):
	user 			= models.OneToOneField(User, primary_key = True)
	theme			= models.CharField(max_length=30, default="dark")
	affiliation		= models.CharField(max_length=30, default="pffl")
	subscription 	= models.DateField(null = False)

class CredentialsModel(models.Model):
	id 				= models.OneToOneField(User, primary_key=True)
	credential 		= CredentialsField()

class Team(models.Model):
	name 			= models.CharField(max_length=30, primary_key=True)
	name_pretty		= models.CharField(max_length=30)

	def __unicode__(self):
		return str(self.name.upper())

	created 		= models.DateTimeField(editable=False)
	modified 		= models.DateTimeField()
	def save(self, *args, **kwargs):
		if not self.created:
			self.created = timezone.now()
		self.modified = timezone.now()
		return super(Team, self).save(*args, **kwargs)

class Conferance(models.Model):
	name 			= models.CharField(max_length=30, primary_key=True)

	def __unicode__(self):
		return str(self.name.upper())

	created 		= models.DateTimeField(editable=False)
	modified 		= models.DateTimeField()
	def save(self, *args, **kwargs):
		if not self.created:
			self.created = timezone.now()
		self.modified = timezone.now()
		return super(Conferance, self).save(*args, **kwargs)

class Division(models.Model):
	name 			= models.CharField(max_length=30, primary_key=True)

	def __unicode__(self):
		return str(self.name.upper())

	created 		= models.DateTimeField(editable=False)
	modified 		= models.DateTimeField()
	def save(self, *args, **kwargs):
		if not self.created:
			self.created = timezone.now()
		self.modified = timezone.now()
		return super(Division, self).save(*args, **kwargs)

class Rank(models.Model):
	value 			= models.IntegerField(primary_key=True)

	def __unicode__(self):
		return str(self.value)

class Schedule(models.Model):
	name 			= models.CharField(max_length=30)
	season 			= models.CharField(max_length=10, null=False)
	year 			= models.IntegerField(null=False)
	generated 		=  models.IntegerField(default=0)
	total 			= models.IntegerField(default=10)
	
	## ALGOS
	# 0 = Match teams by play other divisions
	# 1 = Match teams by play within division
	# 2 = Match teams by against random
	algo 			= models.IntegerField(default=2)

	def __unicode__(self):
		return str(self.name + " (" + self.season + " " + str(self.year) + ")")

	created 		= models.DateTimeField(editable=False)
	modified 		= models.DateTimeField()
	def save(self, *args, **kwargs):
		if not self.id:
			self.created = timezone.now()
		self.modified = timezone.now()
		return super(Schedule, self).save(*args, **kwargs)

class TeamInstance(models.Model):
	schedule 		= models.ForeignKey(Schedule, on_delete=models.CASCADE)
	team 			= models.ForeignKey(Team)
	division 		= models.ForeignKey(Division)
	rank 			= models.ForeignKey(Rank)
	conferance 		= models.ForeignKey(Conferance)
	num_played		= models.IntegerField(default=0)

	def __unicode__(self):
		return str(self.team) + " ............ " + str(self.schedule)

	created 		= models.DateTimeField(editable=False)
	modified 		= models.DateTimeField()
	def save(self, *args, **kwargs):
		if not self.id:
			self.created = timezone.now()
		self.modified = timezone.now()
		return super(TeamInstance, self).save(*args, **kwargs)

class Match(models.Model):
	schedule 		= models.ForeignKey(Schedule, on_delete=models.CASCADE)
	team_one 		= models.ForeignKey(TeamInstance, related_name='team_one', on_delete=models.CASCADE)
	team_two 		= models.ForeignKey(TeamInstance, related_name='team_two', on_delete=models.CASCADE)
	# number 			= models.IntegerField()
	team_one_num	= models.IntegerField()
	team_two_num	= models.IntegerField()

	def __unicode__(self):
		return str(self.team_one.team.name.upper()) + " --vs-- " + str(self.team_two.team.name.upper()) + " ............ " + str(self.schedule)

	created 		= models.DateTimeField(editable=False)
	modified 		= models.DateTimeField()
	def save(self, *args, **kwargs):
		if not self.id:
			self.created = timezone.now()
		self.modified = timezone.now()
		return super(Match, self).save(*args, **kwargs)
