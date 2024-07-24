# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    main.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: aallou-v <aallou-v@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/07/20 16:14:26 by aallou-v          #+#    #+#              #
#    Updated: 2024/07/23 23:15:02 by aallou-v         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from typing import Optional
import discord
from discord import app_commands
from typing import Literal
from UserClass import *
from init_var import BOT_TOKEN

MY_GUILD = discord.Object(id=1261277387664920648)  # replace with your guild id
is_init = False

class MyClient(discord.Client):
	def __init__(self, *, intents: discord.Intents):
		super().__init__(intents=intents)
		self.tree = app_commands.CommandTree(self)

	async def setup_hook(self):
		self.tree.copy_global_to(guild=MY_GUILD)
		await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)



@client.event
async def on_ready():
	if is_init == True:
		return
	print(f'Logged in as {client.user} (ID: {client.user.id})')
	print('------')
	is_init = True
	initiation()

@client.tree.command()
async def update(interaction: discord.Interaction):
	"""Update des donnees"""
	if interaction.guild_id != MY_GUILD.id:
		return await interaction.response.send_message('This command is not available in this guild.', ephemeral=True)
	if interaction.user.id != 580274372695162891:
		return await interaction.response.send_message('You are not allowed to use this command.', ephemeral=True)
	await interaction.response.send_message('Commencement de l\'update', ephemeral=True)
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
		embed = discord.Embed(title='Leaderboard Time Page 1/2', description='This is a leaderboard of logtime', color=0x00ff00)
		embed2 = discord.Embed(title='Leaderboard Time Page 2/2', description='This is a leaderboard of logtime', color=0xff0000)
		embed.description = '```'
		embed2.description = '```'
		classement = 1
		user_entry.sort(key=lambda x: x.logtime_total, reverse=True)
		for entry in user_entry:
			if classement <= 60:
				embed.description += f"{classement} | {entry.login} : {entry.heures} heures, {entry.minutes} minutes\n"
			else:
				embed2.description += f"{classement} | {entry.login} : {entry.heures} heures, {entry.minutes} minutes\n"
			classement += 1
		embed.description += '```'
		embed2.description += '```'
		if effect == True:
			embed.set_footer(text='Vous ne voyez pas votre nom ? C\'est normal, vous n\'êtes pas dans le top 60')
		await interaction.response.send_message(embed=embed, ephemeral=effect)
		if effect == False:
			await interaction.channel.send(embed=embed2)
	elif login is not None:
		await interaction.response.send_message(f"Maintenance en cours ....")
	else:
		await interaction.response.send_message("Command non compris")

@client.tree.command()
@app_commands.describe(login='login de la personne dont on veut voir le rank')
@app_commands.describe(month='mois de la piscine')
@app_commands.describe(year='annee de la piscine')
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
