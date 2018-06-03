# Creates the backup assignment file

import bluetooth
from PyOBEX.client import Client
import pyrebase
import requests
import os
import json
import random

home = os.path.expanduser('~')

url = 'removedurl'

config = {
	'apiKey': 'mykey',
	'authDomain': url + '.firebaseapp.com',
	'databaseURL': 'https://' + url + '.firebaseio.com/',
	'storageBucket': url + '.appspot.com'
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

# Used to convert JSON into the ASCII format
def makeASCIIFromJSON(input):
	if isinstance(input, dict):
		return dict((makeASCIIFromJSON(k), makeASCIIFromJSON(v)) for k, v in input.items())
	elif isinstance(input, list):
		return map(lambda i: makeASCIIFromJSON(i), input)
	elif isinstance(input, str):
		return input.encode('utf-8')
	else:
		return input

print("Pulling data from firebase...")
key = "2018" + str(db.child("TBAcode").get().val())
base_url = "https://www.thebluealliance.com/api/v3/"
headerkey = "X-TBA-Auth-Key"
with open(os.path.join(home, 'Downloads/data/TBAapikey.txt'), 'r') as f:
	authcode = f.read()

eventKeyRequestURL = base_url + "event/"+key+"/matches/simple"

print("Pulling data from TBA...")
matchData = requests.get(eventKeyRequestURL, headers = {headerkey: authcode}).json() 
matchData = makeASCIIFromJSON(matchData)

if type(matchData) == dict:
	print("Error getting data from TBA, check 'TBACode' on firebase! ")

matchIndex = {match['match_number']:matchData.index(match) for match in matchData if match['comp_level']=='qm'}

fullAssignments = {}
for match in matchIndex:
	index = matchIndex[match]
	matchNum = matchData[index]['match_number']
	redTeams = matchData[index]['alliances']['red']['team_keys']
	redTeams = [int(team[3:]) for team in redTeams] # Removes "frc" in "frc1678"
	blueTeams = matchData[index]['alliances']['blue']['team_keys']
	blueTeams = [int(team[3:]) for team in blueTeams] # Removes "frc" in "frc1678"
	teams = redTeams + blueTeams
	assignments = {}
	numScouts = 18
	scouts = ['scout'+str(x) for x in range(1,numScouts+1)]
	# Required list() to prevent availableScouts from being linked to scouts, which causes removed scouts to not be returned
	availableScouts = list(scouts)
	# First block: Assign multiples of 6 to each robot
	for team in teams:
		for x in range(numScouts/6):
			chosenScout = random.choice(availableScouts)
			assignments[chosenScout] = {'team':team, 'alliance':('red' if team in redTeams else 'blue')}
			availableScouts.remove(chosenScout)
	# Second block: Assign remainders after dividing by 6
	extraTeams = random.sample(set(teams), numScouts%len(teams))
	for team in extraTeams:
		chosenScout = random.choice(availableScouts)
		assignments.update({chosenScout:{'team':team,'alliance':('red' if team in redTeams else 'blue')}})
		availableScouts.remove(chosenScout)
	fullAssignments["match"+str(matchNum)] = assignments

data = fullAssignments

# This is the backup that is used in sendBackupFile.py
with open(os.path.join(home, 'Downloads/data/backupAssignments.json'), 'w') as f:
	json.dump(data, f)

# This backup can be directly sent to scout tablets
with open(os.path.join(home, 'Downloads/data/backupAssignments.txt'), 'w') as f:
	f.write(json.dumps(data))

print("")
print("Please run sendBackupFile.py to send the file!")
