# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    main.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: aallou-v <aallou-v@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/07/20 16:14:26 by aallou-v          #+#    #+#              #
#    Updated: 2024/08/10 22:54:02 by aallou-v         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from typing import Optional
import discord
from discord import app_commands
from typing import Literal
from typing import List
from UserClass import UserEntry, update_user
from init_var import BOT_TOKEN, GUILD_ID
import json
from math import ceil

MY_GUILD = discord.Object(id=GUILD_ID)  # replace with your guild id

class MyClient(discord.Client):
	def __init__(self, *, intents: discord.Intents):
		super().__init__(intents=intents)
		self.tree = app_commands.CommandTree(self)

	async def setup_hook(self):
		self.tree.copy_global_to(guild=MY_GUILD)
		await self.tree.sync(guild=MY_GUILD)

user_entry: List[UserEntry] = []
embed: List[discord.Embed] = []

def initiation():
	json_file = open('data.json', 'r')
	data = json.load(json_file)
	user_entry.clear()
	for entry in data:
		user_entry.append(UserEntry(entry['login'], entry['heures'], entry['minutes'], entry['secondes'], entry['logtime_total'], entry['pool_year'], entry['pool_month'], entry['pool_level'], entry['level']))
		print(f"User {entry['login']} added")
	json_file.close()
	for entry in user_entry:
		entry.heures = entry.heures[0]
		entry.minutes = entry.minutes[0]
		entry.secondes = entry.secondes[0]
		entry.logtime_total = entry.logtime_total[0]
		entry.pool_level = entry.pool_level[0]

intents = discord.Intents.default()
client = MyClient(intents=intents)

@client.event
async def on_ready():
	print(f'Logged in as {client.user} (ID: {client.user.id})')
	print('------')
	initiation()

@client.tree.command()
async def update(interaction: discord.Interaction, login: Optional[str] = None):
	"""Update des donnees"""
	if interaction.guild_id != MY_GUILD.id:
		return await interaction.response.send_message('This command is not available in this guild.', ephemeral=True)
	message = 'Commencement de l\'update'
	if login is not None:
		message += f' pour {login}'
	await interaction.response.send_message(message, ephemeral=True)
	if login is not None:
		values = update_user(login)
		if values == 0:
			await interaction.followup.send('Utilisateur non trouve')
		else:
			await interaction.followup.send(f'Utilisateur {login} mis a jour')
	initiation()


@client.tree.command()
@app_commands.describe(login='login de la personne dont on veut voir le temps de logtime')
async def leaderboard(interaction: discord.Interaction, type: Literal['logtime', 'level', 'piscine-level'], login: Optional[str] = None, pool_year: Optional[str] = None, pool_month: Optional[str] = None):
	"""Leaderboard of what you want"""
	if interaction.guild_id is None:
		return await interaction.response.send_message('This command can only be used in a guild.', ephemeral=True)
	if interaction.guild_id != MY_GUILD.id:
		return await interaction.response.send_message('This command is not available in this guild.', ephemeral=True)
	users: List[UserEntry] = []
	for entry in user_entry:
		if pool_year is not None:
			if entry.pool_year[0] != pool_year:
				continue
		if pool_month is not None:
			if entry.pool_month[0] != pool_month:
				continue
		users.append(entry)
	number_of_embed = len(users) / 60
	number_of_embed = ceil(number_of_embed)
	if number_of_embed == 0:
		return await interaction.response.send_message('No data to display', ephemeral=True)
	embed.clear()
	if type == 'logtime':
		users.sort(key=lambda x: x.logtime_total, reverse=True)
	elif type == 'level':
		users.sort(key=lambda x: x.level, reverse=True)
	elif type == 'piscine-level':
		users.sort(key=lambda x: x.pool_level, reverse=True)
	classement = 1
	for i in range(number_of_embed):
		embed.append(discord.Embed(title=f'Leaderboard {type} | Page {i + 1}/{number_of_embed}', description='This is a leaderboard of Logtime', color=0x00ff00))
		embed[i].description = '```'
	for entry in users:
		if pool_year is not None:
			if entry.pool_year[0] != pool_year:
				continue
		if pool_month is not None:
			if entry.pool_month[0] != pool_month:
				continue
		if login is None:
			space = ""
			new_login = entry.login
			if classement < 10:
				space = "   "
			elif classement < 100:
				space = "  "
			elif classement < 1000:
				space = " "
			if len(new_login) < 8:
				while len(new_login) < 8:
					new_login += " "
			message = f"{classement}{space} | {new_login} : "
			if type == 'logtime':
				message += f"{entry.heures}h{entry.minutes}m"
			elif type == 'level':
				message += f"{entry.level}"
			elif type == 'piscine-level':
				message += f"{entry.pool_level}"
			message += '\n'
			embed[(classement - 1) // 60].description += message
		else:
			if entry.login == login:
				message = f"{login} est {classement} dans le classement ({type} : "
				if type == 'logtime':
					message += f"{entry.heures}h{entry.minutes}m"
				elif type == 'level':
					message += f"{entry.level}"
				elif type == 'piscine-level':
					message += f"{entry.pool_level}"
				message += ')'
				return await interaction.response.send_message(message)
		classement += 1
	if login is not None:
		return await interaction.response.send_message(f"{login} n'est pas dans le classement")
	for i in range(number_of_embed):
		embed[i].description += '```'
		await interaction.channel.send(embed=embed[i])

@client.tree.command()
@app_commands.describe(login='login de la personne dont on veut voir le temps de logtime')
async def profile(interaction: discord.Interaction, login: Optional[str] = None):
	"""Look your profile"""
	if interaction.guild_id is None:
		return await interaction.response.send_message('This command can only be used in a guild.', ephemeral=True)
	if interaction.guild_id != MY_GUILD.id:
		return await interaction.response.send_message('This command is not available in this guild.', ephemeral=True)
	if login is None:
		return await interaction.response.send_message('Please provide a login', ephemeral=True)
	for entry in user_entry:
		if entry.login == login:
			embed = discord.Embed(title=f'Profile de {login}', description=f'```Voici le profile de {login}```', color=0x00ff00)
			embed.add_field(name='Logtime', value=f'{entry.heures}h{entry.minutes}m')
			embed.add_field(name='Level', value=f'{entry.level}')
			embed.add_field(name='Pool Level', value=f'{entry.pool_level}')
			embed.add_field(name='Pool Year', value=f'{entry.pool_year}')
			embed.add_field(name='Pool Month', value=f'{entry.pool_month}')
			embed.add_field(name='Pool Exam 00', value=f'{entry.pool_exam_00}')
			embed.add_field(name='Pool Exam 01', value=f'{entry.pool_exam_01}')
			embed.add_field(name='Pool Exam 02', value=f'{entry.pool_exam_02}')
			embed.add_field(name='Pool Exam Final', value=f'{entry.pool_exam_final}')
			embed.add_field(name='Exam 02', value=f'{entry.exam_02}')
			embed.add_field(name='Exam 03', value=f'{entry.exam_03}')
			embed.add_field(name='Exam 04', value=f'{entry.exam_04}')
			embed.add_field(name='Exam 05', value=f'{entry.exam_05}')
			embed.add_field(name='Exam 06', value=f'{entry.exam_06}')
			await interaction.response.send_message(embed=embed)
		

@client.tree.command()
@app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
	"""Says when a member joined."""
	# If no member is explicitly provided then we use the command user here
	member = member or interaction.user

	# The format_dt function formats the date time into a human readable representation in the official client
	await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')


@client.tree.context_menu(name='Show Join Date')
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
	# The format_dt function formats the date time into a human readable representation in the official client
	await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')

client.run(BOT_TOKEN)
