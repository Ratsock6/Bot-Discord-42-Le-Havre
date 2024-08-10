from dataclasses import dataclass, field, asdict, is_dataclass
from typing import List
import requests
import json
from time import sleep
from init_var import PATH_KODO, KEY_ID, KEY_SECRET, KEY_ID2, KEY_SECRET2, KEY_ID3, KEY_SECRET3

data_campus = {
	'grant_type': 'client_credentials',
	'client_id': KEY_ID,
	'client_secret': KEY_SECRET,
}

data_first = {
	'grant_type': 'client_credentials',
	'client_id': KEY_ID2,
	'client_secret': KEY_SECRET2,
}

data_second = {
	'grant_type': 'client_credentials',
	'client_id': KEY_ID3,
	'client_secret': KEY_SECRET3,
}

response_campus = requests.post('https://api.intra.42.fr/oauth/token', data=data_campus)
response_first = requests.post('https://api.intra.42.fr/oauth/token', data=data_first)
response_second = requests.post('https://api.intra.42.fr/oauth/token', data=data_second)

token_campus = response_campus.json()['access_token']
token_first_request = response_first.json()['access_token']
token_second_request = response_second.json()['access_token']
#token = subprocess.check_output(PATH_KODO, shell=True, text=True).strip()


headers_campus = {
	'Authorization': 'Bearer ' + token_campus,
}

headers_first_request = {
	'Authorization': 'Bearer ' + token_first_request,
}

headers_second_request = {
	'Authorization': 'Bearer ' + token_second_request,
}

params = {
	'begin_at': '2010-12-30T00:00:00.000Z',
	'end_at': '2030-12-31T23:59:59.999Z',
}

params2 = {
	'filter[staff?]' : 'false',
	'filter[pool_year]' : '2023',
	'filter[pool_month]' : 'august',
	'page': 0,
	'per_page': 100,
}

@dataclass
class ProjectEntry:
	name: str = ""
	state: str = ""
	note: str = ""
	finish: bool = False
	occurence: int = 0

@dataclass
class UserEntry:
	login: str = ""
	heures: int = 0
	minutes: int = 0
	secondes: float = 0.0
	logtime_total: float = 0.0
	pool_year: str = ""
	pool_month: str = ""
	pool_level: float = 0.0
	level: float = 0.0
	project_number: int = 0
	profile_img: str = ""
	profile_img_micro: str = ""

	def to_dict(self):
		# Convertit la liste de ProjectEntry en une liste de dictionnaires
		return {
			"login": self.login,
			"heures": self.heures,
			"minutes": self.minutes,
			"secondes": self.secondes,
			"logtime_total": self.logtime_total,
			"pool_year": self.pool_year,
			"pool_month": self.pool_month,
			"pool_level": self.pool_level,
			"level": self.level,
			"project_number": self.project_number,
			"project": [asdict(project) for project in self.project if isinstance(project, ProjectEntry)],
			"profile_img": self.profile_img,
			"profile_img_micro": self.profile_img_micro
		}

user_entry: List[UserEntry] = []

def update_all():
	user_entry.clear()
	print("Début de l'initialisation cela peut prendre un certain temps")
	year = 2024
	is_boucle = True
	while is_boucle:
		params2['filter[pool_year]'] = str(year)
		print(f"Année {params2['filter[pool_year]']}")
		year += 1
		x = 0
		while True:
			x += 1
			params2['page'] = x
			resp = requests.get('https://api.intra.42.fr/v2/campus/le-havre/users', headers=headers_campus, params=params2)
			if resp.status_code != 200:
				print(f"Erreur Campus Users {resp.status_code}")
				is_boucle = False
				break
			sleep(1)
			if resp.json() == []:
				is_boucle = False
				break
			count = 0
			for user in resp.json():
				print(f"Traitement de {user['login']}")
				user_entry.append(create_user(user['login']))
				sleep(0.5)
				count += 1
			if count < 100:
				break
	print(f"Nombre d'utilisateur : {len(user_entry)}")
	print(f"-------------------------")
	for entry in user_entry:
		if entry is None:
			continue
		print(f"Login: {entry.login}")
	with open('data.json', 'w') as f:
		f.write(json.dumps([entry.__dict__ for entry in user_entry if entry is not None], indent=4))
	print("Fin de l'initialisation")

def update_user_entry_by_json():
	json_file = open('data.json', 'r')
	data = json.load(json_file)
	user_entry.clear()
	for entry in data:
		user_entry.append(UserEntry(entry['login'], entry['heures'], entry['minutes'], entry['secondes'], entry['logtime_total'], entry['pool_year'], entry['pool_month'], entry['pool_level'], entry['level']))
		print(f"User {entry['login']} added")
	json_file.close()

def update_user(login):
	print(f"Update de {login}")
	update_user_entry_by_json()
	for entry in user_entry:
		if entry.login == login:
			find = True
			user_entry.remove(entry)
			user_entry.append(create_user(login))
			with open('data.json', 'w') as f:
				f.write(json.dumps([entry.__dict__ for entry in user_entry if entry is not None], indent=4))
			return 1
	if not find:
		return 0
	return 1
	


def create_user(login):
	final_value = UserEntry()
	logtime_request = requests.get('https://api.intra.42.fr/v2/users/' + login + '/locations_stats', headers=headers_first_request, params=params)
	if logtime_request.status_code != 200:
		print(f"Erreur Locations Stats {logtime_request.status_code}")
		return
	donnees = json.loads(logtime_request.text)
	hours = 0
	minutes = 0
	seconds = 0.0
	for i in donnees:
		values = donnees[i].split(':')
		hours += int(values[0])
		minutes += int(values[1])
		seconds += float(values[2])
	minutes += int(seconds / 60)
	seconds = seconds % 60
	hours += int(minutes / 60)
	minutes = minutes % 60
	rank = requests.get('https://api.intra.42.fr/v2/users/' + login, headers=headers_second_request)
	if rank.status_code != 200:
		print(f"Erreur User {rank.status_code}")
		return
	data = json.loads(rank.text)
	if data['cursus_users'] is None or len(data['cursus_users']) == 0:
		print(f"Erreur {login} n'a pas de cursus")
		return
	pool_level = data['cursus_users'][0]['level']
	if len(data['cursus_users']) > 1:
		level = data['cursus_users'][1]['level']
	else:
		level = -1
	pool_year = 'None'
	pool_month = 'None'
	if data['pool_year'] is None or data['pool_month'] is None:
		print(f"Erreur {login} n'a pas de piscine")
	else:
		pool_year = data['pool_year']
		pool_month = data['pool_month']
	final_value.profile_img = data['image']['link']
	final_value.profile_img_micro = data['image']['versions']['micro']
	final_value.login=login
	final_value.heures=hours,
	final_value.minutes=minutes,
	final_value.secondes=seconds,
	final_value.logtime_total=(hours*60*60 + minutes*60 + seconds),
	final_value.pool_year=pool_year,
	final_value.pool_month=pool_month,
	final_value.pool_level=pool_level,
	final_value.level=level
	# rank = requests.get('https://api.intra.42.fr/v2/users/' + login + '/projects_users', headers=headers_campus)
	# if rank.status_code != 200:
	# 	print(f"Erreur {rank.status_code}")
	# 	return
	# data = json.loads(rank.text)
	# if data is not None:
	# 	for iterate in data:
	# 		final_value.project_number += 1
	return final_value

def get_user(login):
	for entry in user_entry:
		if entry.login == login:
			return entry
	return None

if __name__ == "__main__":
	update_all()