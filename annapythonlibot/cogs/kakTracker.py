# tracker.py

# Tracking kakera


# Config
import config.config as config
# This is the discord
import discord
from discord.ext import commands
# Pretty print
# import pprint
# Regex
import re
# json
import json
# Async
import asyncio


# Our track cog
class TrackCog(commands.Cog, name="Tracking"):
	"""TrackCog"""

	# Allows us to have bot defined and passed in
	def __init__(self, bot):
		self.bot = bot

		# # Config
		# self.CONFIG_var = ctxvar.ContextVar('CONFIG')
		# self.CONFIG_var.set(config)

		with open("data.json", "r") as file:
			dataJSON = json.loads(file.read())


		# Data
		self.data = {
			'channel': None,
			'last_user': None,
			'data': dataJSON
		}

		# Constants
		self.ROLL_COMMANDS = ["$" + a + b for a in "whm" for b in list("abg") + ['']]

		self.KAKERA_FULL_NAME = [
			'<:kakeraP:609264226342797333>',
			'<:kakera:469791929106956298>',
			'<:kakeraT:609264247645536276>',
			'<:kakeraG:609264237780402228>',
			'<:kakeraY:605124267574558720>',
			'<:kakeraO:605124259018178560>',
			'<:kakeraR:605124263917256836>',
			'<:kakeraW:608193418698686465>'
		]

		self.KAKERA_NAME = ["kakera" + a for a in ['P', ''] + list("TGYORW")]

		self.KAKERA_EMOTES = {
			**{self.KAKERA_FULL_NAME[i]: self.KAKERA_NAME[i] for i in range(len(self.KAKERA_NAME))},
			**{self.KAKERA_NAME[i]: self.KAKERA_FULL_NAME[i] for i in range(len(self.KAKERA_NAME))}
		}

		self.gen_template = lambda KAKERA_NAME: {field: {kak: 0 for kak in KAKERA_NAME } for field in "rolled claimed".split()}

		self.MY_KAKERA_FULL_NAME = [
			"<:kakeraP:739401967163539517>",
			"<:kakera:739401967276785694>",
			"<:kakeraT:739401967410872360>",
			"<:kakeraG:739401967264333885>",
			"<:kakeraY:739401967406809129>",
			"<:kakeraO:739401966911881269>",
			"<:kakeraR:739401967280848936>",
			"<:kakeraW:739401967364734986>"
		]

		self.KAKERA_STATS_TEMPLATE = " ".join(["%sx" + kak for kak in self.MY_KAKERA_FULL_NAME])



	# Attempt to read emotes for tracking rolls
	@commands.Cog.listener()
	async def on_message(self, message):


		# BASICS

		# If the bot is reading it's own message
		if message.author == self.bot.user:
			return

		# Lock on this channel only
		if message.content.lower() == "lock on this channel":
			self.data['channel'] = message.channel
			await message.channel.send("Locked on: " + str(self.data['channel']))
			return

		# The block
		if message.channel != self.data['channel']:
			return


		# Checks for embeds
		if False and len(message.embeds) > 0:
			pprint.pprint(message.embeds[0].to_dict()['description'])
		

		# CORE


		# Keep track of the person that sent the last command
		if message.content.lower() in self.ROLL_COMMANDS:
			# self.data['last_user'] = message.author.id
			self.data['last_user'] = message.author.name
			return


		# print(message.author, message.content, message.reactions)
		# Mudamaid 18#0442 <:kakeraY:605124267574558720>**Larypie +406** ($k) []

		kakera_collect = re.search('(<:kakera[PTGYORW]?:\d+>)\*\*(.+) \+\d+\*\* \(\$k\)', message.content)

		# Count when the kakera was collected
		if kakera_collect:

			# Figureout which kakera it was; convert from full name to name
			kakera_type = kakera_collect.group(1)
			kakera_type = re.search('<:(kakera[PTGYORW]?):\d+>', kakera_type).group(1)

			name = kakera_collect.group(2)

			# If there is no data for that user then make an empty data sheet
			if name not in self.data['data']:
				self.data['data'][name] = self.gen_template(self.KAKERA_NAME)

			# Update the data on that user
			self.data['data'][name]['claimed'][kakera_type] += 1
			print("Added Claim")
			await message.channel.send("you claimed!")
			return


		# Output the running data
		if message.content.lower() == "anna li stats":

			embed = discord.Embed(
				# title='Title',
				# description='description',
				# url='https://cdn.discordapp.com/attachments/618692088137252864/739352223619743882/bbffbb.png',
				colour=discord.Colour.red()
			)

			# embed.set_image(url='https://cdn.discordapp.com/attachments/618692088137252864/739351037781213204/ffbbff.png')
			# embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/618692088137252864/739352396144312360/bbbbff.png')
			# embed.set_footer(text='footer')

			embed.set_author(name='Anna Li stats')


			# For each user
			for user in self.data['data'].items():

				name, value = user

				# Print their rolls and claims
				embed.add_field(
					name=name + " rolls",
					value=self.KAKERA_STATS_TEMPLATE % tuple(["**" + str(v) + "**" for v in value['rolled'].values()]),
					inline=False
				)
				embed.add_field(
					name=name + " claims",
					value=self.KAKERA_STATS_TEMPLATE % tuple(["**" + str(v) + "**" for v in value['claimed'].values()]),
					inline=True
				)


			# await ctx.send()
			await message.channel.send(embed=embed)
			return

		# Save the data
		if message.content.lower() == "anna li save":
			with open("data.json", 'w') as file:
				file.write(json.dumps(self.data['data']))
			await message.channel.send("saved")
			return


	# When the bot notices a reaction to a message
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):

		message = reaction.message

		# BASICS

		# If the bot is reading it's own message
		if message.author == self.bot.user:
			return

		# Only bot messages matter
		if message.author.bot == False:
			return

		# The block (Lock set up in the messages events)
		if message.channel != self.data['channel']:
			return


		# CORE


		# What does kakera reaction look like in str form
		# print(str(reaction))

		# If it isn't real kakera
		if str(reaction) not in self.KAKERA_FULL_NAME:
			return

		# Extract out name of the kakera
		kakera_reaction = re.search('<:(kakera[PTGYORW]?):\d+>', str(reaction))

		# Increment kakera count
		if kakera_reaction:

			# If there is more than 1 valid react to this message ignore it
			if message.reactions[0].count != 1:
				return

			# Who rolled last
			roller = self.data['last_user']

			# Extract out name of the kakera
			kakera = kakera_reaction.group(1)

			# If there is no data for that user then make an empty data sheet
			if roller not in self.data['data']:
				self.data['data'][roller] = self.gen_template(self.KAKERA_NAME)

			# Update the data on that user
			self.data['data'][roller]['rolled'][kakera] += 1
			print("Added")
			return


		# MISC

		# If the message is what we expect then reply to it
		if message.content == "React":
			await message.channel.send(reaction)
			return



# Give the cog to the bot
def setup(bot):
	bot.add_cog(TrackCog(bot))