from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
import datetime
from django.utils import formats
import json

from pffl.models import *
from pffl.forms import *
from pffl.apitools import *
from pffl.scheduletools import *

import requests, time
from time import *
from django.db import transaction

@login_required
def home(request):
    context = {
    	'schedules': Schedule.objects.all().order_by('-created')
    }
    return render(request, "home.html", context)

@transaction.atomic
def register(request):
	context = {}

	# Just display the registration form if this is a GET request.
	if request.method == 'GET':
		context['form'] = RegistrationForm()
		return render(request, 'register.html', context)

	# Creates a bound form from the request POST parameters and makes the 
	# form available in the request context dictionary.
	form = RegistrationForm(request.POST)
	context['form'] = form

	# Validates the form.
	if not form.is_valid():
		return render(request, 'register.html', context)

	# If we get here the form data was valid.  Register and login the user.
	new_user = User.objects.create_user(username=form.cleaned_data["email"],
										email=form.cleaned_data["email"],
										first_name=form.cleaned_data["first_name"],
										last_name=form.cleaned_data["last_name"],
										password=form.cleaned_data["password1"])
	new_user.save()

	new_user = authenticate(username=form.cleaned_data["email"],
							password=form.cleaned_data["password1"])
	auth_login(request, new_user)

	# add user profile
	new_profile = UserProfile.objects.create(user = new_user, 
											subscription=datetime.date.today())
	new_profile.save()

	return HttpResponseRedirect(reverse('home'))

@login_required
def profile(request):
	context = {}
	if request.method == "POST":
		try:
			fname = request.POST.__getitem__('fname')
			lname = request.POST.__getitem__('lname')
			affiliation = request.POST.__getitem__('affiliation')
			theme = request.POST.__getitem__('theme')

			profile, created = UserProfile.objects.get_or_create(user = request.user)
			user = request.user
			profile.affiliation = affiliation
			profile.theme = theme
			user.first_name = fname
			user.last_name = lname
			user.save()
			profile.save()
		except:
			context['error_message'] = "Invalid submission."

	if is_authorized(request):
		context['authorized'] = True
	return render(request, "profile.html", context)

@login_required
def authorize(request):
	if is_authorized(request):
		return HttpResponseRedirect(reverse('profile'))
	return authorize_google(1, request)

@login_required
def auth_return(request):
	if authorize_google(2, request):
		return HttpResponseRedirect(reverse('auth_success'))
	else:
		return HttpResponseRedirect(reverse('auth_fail'))

@login_required
def auth_success(request):
	HttpResponseRedirect(reverse('profile'))

@login_required
def auth_fail(request):
	context = { 'error_message':"There was an issue connecting with your Google account" }
	return render(request, "profile.html", context)

@login_required
def create_schedule(request):
	context = {}
	return render(request, "create_schedule.html", context)

@login_required
def view_schedule(request, schedule_id):
	context = {}
	try:
		schedule = Schedule.objects.get(id=schedule_id)
		context['schedule'] = schedule
		context['table'] = createTable(schedule)
		context['num_matches'] = range(1,schedule.total+1)
	except:
		context['error'] = True
	return render(request, "view_schedule.html", context)

@login_required
def import_sheet(request):
	error_messages = [
		"Something went wrong. Ensure that the URL is correct and try again.",
		"You have not yet linked your account with Google Drive yet.\nGo to your profile page to link your account.",
		"Invalid request."
	]
	response_text = {
		"error" : True,
		"error_message" : "Request was not a post"
	}
	if is_authorized(request):
		if request.method == "POST":
			http = get_credentials(request)
			url = request.POST.__getitem__('sheet_url')
			try:
				response_text['values'] = get_sheet(http, url, 'A2:D')
				response_text['error'] = False
			except:
				response_text['error_message'] = error_messages[0]
		else:
			response_text['error_message'] = error_messages[2]
	else:
		response_text['error_message'] = error_messages[1]

	return HttpResponse(json.dumps(response_text), content_type='application/json')

@login_required
def generate_schedule(request):
	error_messages = [
		"An error occured while generating the schedule."
	]
	response_text = {
		"error" : True,
		"error_message" : "Request was not a post"
	}
	if request.method == "POST":
		teams = json.loads(request.POST.__getitem__('teams'))
		to_gen = int(request.POST.__getitem__('to_gen'))
		total = int(request.POST.__getitem__('total'))
		algo = int(request.POST.__getitem__('algo'))
		season = request.POST.__getitem__('season')
		year = int(request.POST.__getitem__('year'))
		name = request.POST.__getitem__('name')
		override = request.POST.__getitem__('override')
		schedule = request.POST.__getitem__('schedule_id')

		print "***"
		print to_gen
		print total
		print algo
		print season
		print year
		print name
		print override
		print schedule

		if schedule: # update existing
			schedule = Schedule.objects.get(id=schedule)
			schedule.name = name
			schedule.season = season
			schedule.year = year
			schedule.total = total
			schedule.algo = algo
			if override:
				schedule.match_set.all().delete() # clears existing games
				schedule.generated = 0
			schedule.generated += to_gen

		else: # create new
			schedule = Schedule.objects.create(name = name,
												season = season,
												year = year,
												algo = algo,
												total = total,
												generated = to_gen)
		schedule.save()
		
		for team in teams:
			updateAllFields(team)
			createInstance(schedule, team)

		generateSchedule(schedule)

		response_text['error'] = False
		response_text['schedule_id'] = schedule.id
		print str(schedule.id) + " **** ID ****"
	return HttpResponse(json.dumps(response_text), content_type='application/json')

@login_required
def export_schedule(request, schedule_id):
	messages = [
		"An error occured while exporting the schedule.",
		"You have not yet linked your account with Google Drive yet.",
		"Invalid request.",
		"You successfully exported your schedule to Google!"
	]
	response_text = {
		"error" : True,
		"message" : "Request was not a post"
	}
	if is_authorized(request):
		if request.method == "POST":
			http = get_credentials(request)
			# try:
			schedule = Schedule.objects.get(id=schedule_id)
			http = get_credentials(request)
			create_sheet(http, forExport(createTable(schedule)), schedule)

			response_text['message'] = messages[3]
			response_text['sheet_url'] = 'To Come...'
			response_text['error'] = False
			# except Exception,e: 
			# 	print str(e)
			# 	response_text['message'] = messages[0]
		else:
			response_text['message'] = messages[2]
	else:
		response_text['message'] = messages[1]

	return HttpResponse(json.dumps(response_text), content_type='application/json')

