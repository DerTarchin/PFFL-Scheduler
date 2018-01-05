import random

from pffl.models import *
from pffl.forms import *
from pffl.apitools import *

## DATABASE MANAGEMENT
def updateAllFields(fields):
	updateTeam(fields[0]) #name
	updateConferance(fields[1]) #conferance
	updateDivision(fields[2]) #division
	updateRank(fields[3]) #rank

def updateTeam(name):
	new_team, _ = Team.objects.update_or_create(name = name.lower(),
												name_pretty = name)
	new_team.save()

def updateConferance(name):
	new_conferance, _ = Conferance.objects.update_or_create(name = name.lower())
	new_conferance.save()

def updateDivision(name):
	new_division, _ = Division.objects.update_or_create(name = name.lower())
	new_division.save()

def updateRank(value):
	new_rank, _ = Rank.objects.update_or_create(value = value)
	new_rank.save()


## DATABASE INFO
def getTeam(name):
	try:
		return Team.objects.get(name=name.lower())
	except:
		return None

def getConferance(name):
	try:
		return Conferance.objects.get(name=name.lower())
	except:
		return None

def getConferanceSet(schedule):
	try:
		con_set = []
		for team in schedule.teaminstance_set.all():
			if not team.conferance in con_set:
				con_set.append(team.conferance)
		return con_set
	except:
		return None

def getDivision(name):
	try:
		return Division.objects.get(name=name.lower())
	except:
		return None

def getDivisionSet(schedule):
	try:
		div_set = []
		for team in schedule.teaminstance_set.all():
			if not team.division in div_set:
				div_set.append(team.division)
		return div_set
	except:
		return None

def getRank(value):
	try:
		return Rank.objects.get(value=value)
	except:
		return None


## METADATA
def hasPlayedAgainst(team_one, team_two):
	try:
	    match = Match.objects.get(team_one=team_one, team_two=team_two)
	    return True
	except:
		try:
			match = Match.objects.get(team_one=team_two, team_two=team_one)
			return True
		except:
			pass
	return False

def getNumPlayed(team):
	amount = 0
	for match in team.team_one.all():
		amount+=1
	for match in team.team_two.all():
		amount+=1
	return amount

def getMatches(team, num):
	matches = [None]*num
	for match in team.team_one.all():
		matches[match.team_one_num-1] = match.team_two
	for match in team.team_two.all():
		matches[match.team_two_num-1] = match.team_one
	return matches

def getMatchType(team_one, team_two):
	if team_one.division == team_two.division:
		return "in_div"
	elif team_one.conferance == team_two.conferance:
		return "non_div"
	else:
		return "non_con"



## SCHEDULE
def createInstance(schedule, fields):
	instance, _ = TeamInstance.objects.update_or_create(schedule = schedule,
											team = getTeam(fields[0]), #name
											conferance = getConferance(fields[1]), #conferance
											division = getDivision(fields[2]), #division
											rank = getRank(fields[3])) #rank
	instance.save()

def createMatch(schedule, team, opp):
	team.num_played = getNumPlayed(team) + 1
	team.save()
	opp.num_played = getNumPlayed(opp) + 1
	opp.save()
	new_match = Match.objects.create(schedule = schedule,
									team_one = team,
									team_two = opp,
									team_one_num = team.num_played,
									team_two_num = opp.num_played)
	new_match.save()

def findOpponent(team, rest, max_gen, ignore_num_played=False):
	for opp in rest.order_by('?'):
		if getNumPlayed(opp) < max_gen and not hasPlayedAgainst(team, opp):
			return opp
		if ignore_num_played and not hasPlayedAgainst(team, opp):
			return opp
	return None

def generateSchedule(schedule):
	total = schedule.total
	algo = schedule.algo
	to_gen = schedule.generated

	if algo == 0: # other divisions
		teams = schedule.teaminstance_set.all()
		for match_num in range(1, to_gen+1):
		# if True:
			for team in teams:
				if getNumPlayed(team) >= to_gen:
					continue
				rest = teams.exclude(team = team.team)

				# ==rank, !=con, !=div
				rest_1 = rest.exclude(conferance = team.conferance)
				rest_1 = rest.exclude(division = team.division)
				rest_1 = rest.filter(rank = team.rank)
				opp = findOpponent(team, rest_1, to_gen)
				if opp:
					createMatch(schedule, team, opp)
					continue

				# ==rank, ==con, !=div
				rest_2 = rest.exclude(division = team.division)
				rest_2 = rest.filter(rank = team.rank, conferance = team.conferance)
				opp = findOpponent(team, rest_2, to_gen)
				if opp:
					createMatch(schedule, team, opp)
					continue

				# rank+/-1, ~con, !=div
				rest_3 = rest.exclude(division = team.division)
				try:
					rest_3 = rest.exclude(rank__gt = getRank(team.rank.value+1))
				except:
					pass
				try:
					rest_3 = rest.exclude(rank__lt = getRank(team.rank.value-1))
				except:
					pass
				opp = findOpponent(team, rest_3, to_gen)
				if opp:
					createMatch(schedule, team, opp)
					continue

				# ~rank, ~con, !=div
				rest_4 = rest.exclude(division = team.division)
				opp = findOpponent(team, rest_4, to_gen)
				if opp:
					createMatch(schedule, team, opp)
					continue

				# ~rank, ~con, ~div
				rest_5 = rest
				opp = findOpponent(team, rest_5, to_gen)
				if opp:
					createMatch(schedule, team, opp)
					continue

				# match against another team that already filled max gen
				# ==rank, ~con, !=div
				rest_6 = rest.exclude(division = team.division)
				try:
					rest_6 = rest.exclude(rank__gt = getRank(team.rank.value+1))
				except:
					pass
				try:
					rest_6 = rest.exclude(rank__lt = getRank(team.rank.value-1))
				except:
					pass
				opp = findOpponent(team, rest_6, to_gen, ignore_num_played=True)
				if opp:
					createMatch(schedule, team, opp)
					continue

def createTable(schedule):
	table = []
	for conferance in getConferanceSet(schedule):
		for division in getDivisionSet(schedule):
			for team in schedule.teaminstance_set.filter(conferance=conferance,
													division=division):
				table.append({'team':team, 'matches':getMatches(team, schedule.total)})
	return table

def forExport(table):
	data = []
	for team_data in table:
		row = [
			{'value': team_data['team'].team.name, 'format': 'info'},
			{'value': team_data['team'].conferance.name, 'format': 'info'},
			{'value': team_data['team'].division.name, 'format': 'info'},
			{'value': team_data['team'].rank.value, 'format': 'info'},
		]
		for opp in team_data['matches']:
			if opp:
				row.append({
					'value': opp.team.name + " (" + str(opp.rank.value) + ")",
					'format': getMatchType(team_data['team'], opp)
				})
			else:
				row.append({ 'value': '', 'format': '' })
		data.append(row)
	return data


