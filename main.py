# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    main.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: aallou-v <aallou-v@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/07/20 16:14:26 by aallou-v          #+#    #+#              #
#    Updated: 2024/07/24 22:59:47 by aallou-v         ###   ########.fr        #
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
	if interaction.user.id != 580274372695162891:
		return await interaction.response.send_message('You are not allowed to use this command.', ephemeral=True)
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
@app_commands.describe(since='2023-12-30')
async def logtime(interaction: discord.Interaction, login: Optional[str] = None, since: Optional[str] = None):
	"""Leaderboard of logtime"""
	effect = False
	if login is None and since is None:
		if interaction.guild_id is None:
			return await interaction.response.send_message('This command can only be used in a guild.', ephemeral=True)
		if interaction.guild_id != MY_GUILD.id:
			return await interaction.response.send_message('This command is not available in this guild.', ephemeral=True)
		if interaction.user.id != 580274372695162891:
			effect = True
		calcul = len(user_entry) / 60
		number_embed = int(calcul)
		user_entry.sort(key=lambda x: x.logtime_total, reverse=True)
		classement = 1
		for i in range(number_embed):
			embed.append(discord.Embed(title=f'Leaderboard Time Page {i+1}/{number_embed}', description='This is a leaderboard of logtime', color=0x00ff00))
			embed[i].description = '```'
			for entry in user_entry[i*60:(i+1)*60]:
				embed[i].description += f"{classement} | {entry.login} : {entry.heures} heures, {entry.minutes} minutes\n"
				classement += 1
			embed[i].description += '```'
			if effect == True:
				embed[i].set_footer(text='Vous ne voyez pas votre nom ? C\'est normal, vous n\'êtes pas dans le top 60')
				await interaction.response.send_message(embed=embed[i], ephemeral=effect)
				return
		await interaction.response.send_message(embed=embed[0], ephemeral=effect)
		for i in range(number_embed):
			if i != 0:
				await interaction.channel.send(embed=embed[i])
	elif login is not None:
		await interaction.response.send_message(f"Maintenance en cours ....", ephemeral=True)
	else:
		await interaction.response.send_message("Command non compris")

@client.tree.command()
@app_commands.describe(login='login de la personne dont on veut voir le rank')
@app_commands.describe(month='Mois de la piscine')
@app_commands.describe(year='Annee de la piscine')
async def rank(interaction: discord.Interaction, login: Optional[str] = None, month: Literal['july', 'august', 'september', 'all'] = None, year: Literal['2023', '2024', '2025', '2026', 'all'] = None):
	"""Leaderboard of level"""
	effect = False
	if login is None:
		if interaction.guild_id is None:
			return await interaction.response.send_message('This command can only be used in a guild.', ephemeral=True)
		if interaction.guild_id != MY_GUILD.id:
			return await interaction.response.send_message('This command is not available in this guild.', ephemeral=True)
		if interaction.user.id != 580274372695162891:
			effect = True
		embed = discord.Embed(title='Leaderboard Level Page 1/2', description='This is a leaderboard of Piscine Level', color=0x00ff00)
		embed2 = discord.Embed(title='Leaderboard Level Page 2/2', description='This is a leaderboard of Piscine Level', color=0xff0000)
		embed.description = '```'
		embed2.description = '```'
		classement = 1
		user_entry.sort(key=lambda x: x.pool_level, reverse=True)
		for entry in user_entry:
			if month == 'all' and year == 'all':
				if classement <= 60:
					embed.description += f"{classement} | {entry.login} : {entry.level} level\n"
				else:
					embed2.description += f"{classement} | {entry.login} : {entry.level} level\n"
				classement += 1
			elif month == 'all' and year != 'all':
				if entry.pool_year != year:
					continue
				if classement <= 60:
					embed.description += f"{classement} | {entry.login} : {entry.level} level\n"
				else:
					embed2.description += f"{classement} | {entry.login} : {entry.level} level\n"
				classement += 1
			elif month != 'all' and year == 'all':
				if entry.pool_month != month:
					continue
				if classement <= 60:
					embed.description += f"{classement} | {entry.login} : {entry.level} level\n"
				else:
					embed2.description += f"{classement} | {entry.login} : {entry.level} level\n"
				classement += 1
			else:
				if entry.pool_month != month or entry.pool_year != year:
					continue
				if classement <= 60:
					embed.description += f"{classement} | {entry.login} : {entry.level} level\n"
				else:
					embed2.description += f"{classement} | {entry.login} : {entry.level} level\n"
				classement += 1
		embed.description += '```'
		embed2.description += '```'
		if effect == True:
			embed.set_footer(text='Vous ne voyez pas votre nom ? C\'est normal, vous n\'êtes pas dans le top 60')
		await interaction.response.send_message(embed=embed, ephemeral=effect)
		if effect == False:
			await interaction.channel.send(embed=embed2)
	else:
		classement = 1
		find = False
		for entry in user_entry:
			if entry.login == login:
				find = True
				break
			classement += 1
		if find == True:
			return await interaction.response.send_message(f"{login} est {classement} dans le classement (level : {entry.level})")
		await interaction.response.send_message(f"{login} n'est pas dans le classement")
		
		

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
