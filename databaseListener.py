#!/usr/bin/python -p
# Configuration: sudo cp databaseListener.service /etc/systemd/system/databaseListener.service
# systemctl daemon-reload
# systemctl enable databaseListener.service
# systemctl start databaseListener.service
# systemctl status databaseListener.service
import os
import pyrebase
import subprocess

home = os.path.expanduser('~')

url = 'scouting-2018-9023a'

config = {
	'apiKey': 'mykey',
	'authDomain': url + '.firebaseapp.com',
	'databaseURL': 'https://' + url + '.firebaseio.com/',
	'storageBucket': url + '.appspot.com'
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

def stream_handler(message):
	if type(message["data"]) == int:
		with open(os.path.join(home, '/files/Robotics/2018/Scout-Manager-2018/lastSent.txt'), 'r') as f:#'Downloads/data/lastSent.txt'), 'r') as f:
			match = f.read()
		if match == "":
			match = 0
		if message["data"] != int(match):
			subprocess.call(os.path.join(home, "Desktop/sendAssignments.py"), shell=True)
			with open(os.path.join(home, 'Downloads/data/lastSent.txt'), 'w') as f:
				f.write(str(message["data"]))

my_stream = db.child("scouts/match").stream(stream_handler)