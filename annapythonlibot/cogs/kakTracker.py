# tracker.py

# Tracking kakera


# Config
import config.config as config
# This is the discord
import discord
from discord.ext import commands
# Regex
import re
# Time
import time
import datetime
# mongodb
import pymongo


def utc_to_local(utc_dt):
	return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

# Our track cog
class TrackCog(commands.Cog, name="Tracking"):
	"""TrackCog"""

	# Allows us to have bot defined and passed in
	def __init__(self, bot):
		self.bot = bot

		# Connect the mongodb client
		self.client = pymongo.MongoClient(config.DB_URI)
		self.db = self.client.kakera

		# Data
		self.data = {
			'channel': config.STATS_TRACKER_CHANNEL_ID,
			'last_user': None
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

		self.MY_KAKERA_EMOTES = {
			**{self.MY_KAKERA_FULL_NAME[i]: self.KAKERA_NAME[i] for i in range(len(self.KAKERA_NAME))},
			**{self.KAKERA_NAME[i]: self.MY_KAKERA_FULL_NAME[i] for i in range(len(self.KAKERA_NAME))}
		}

		self.KAKERA_STATS_TEMPLATE = " ".join(["%s" + kak for kak in self.MY_KAKERA_FULL_NAME])
		# self.KAKERA_STATS_TEMPLATE = " ".join(["%sx " + kak for kak in self.MY_KAKERA_FULL_NAME])



	# Attempt to read emotes for tracking rolls
	@commands.Cog.listener()
	async def on_message(self, message):


		# If the bot is reading it's own message
		if message.author == self.bot.user:
			return

		# The block
		if message.channel != self.data['channel']:
			return


		# Keep track of the person that sent the last command
		if message.content.lower() in self.ROLL_COMMANDS:
			# self.data['last_user'] = message.author.id
			self.data['last_user'] = message.author.name
			return

		# pprint.pprint(message.embeds[0].to_dict()['description'])
		# print(message.author, message.content, message.reactions)
		# Mudamaid 18#0442 <:kakeraY:605124267574558720>**Larypie +406** ($k) []

		kakera_collect = re.search('(<:kakera[PTGYORW]?:\d+>)(\(Free\) )?\*\*(.+) \+(\d+)\*\* \(\$k\)', message.content)

		# Count when the kakera was collected
		if kakera_collect:

			# Figureout which kakera it was; convert from full name to name
			kakera_type = kakera_collect.group(1)
			kakera_type = re.search('<:(kakera[PTGYORW]?):\d+>', kakera_type).group(1)

			name = kakera_collect.group(3)

			await message.channel.send("you claimed: " + str(kakera_collect.group(4)))

			# Prepare doc
			doc = {
				'time': 	datetime.datetime.utcnow(),
				'roller': 	self.data['last_user'],
				'claimer':	name,
				'kakera': 	kakera_type,
				'value': 	int(kakera_collect.group(4))
			}

			# Upload data to server
			self.db.kakera_claimed.insert_one(doc)
			return


	# When the bot notices a reaction to a message
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):

		message = reaction.message

		# If the bot is reading it's own message
		if message.author == self.bot.user:
			return

		# Only bot messages matter
		if message.author.bot == False:
			return

		# The block (Lock set up in the messages events)
		if message.channel != self.data['channel']:
			return

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

			# Prepare doc
			doc = {
				'time': 	datetime.datetime.utcnow(),
				'roller': 	self.data['last_user'],
				'kakera': 	kakera
			}

			# Upload data to server
			self.db.kakera_rolled.insert_one(doc)

			print("Added")
			return


	@commands.command(
		name='stats',
		aliases=['s'],
		brief='Kakera stas',
		description='Reports the kakera roll and claim stats!',
		help='days (int): how many days back to search',
		usage='days')
	async def _stats(self, ctx, days=1):

		time_start = time.time()

		# Make the embed
		embed = discord.Embed(
			colour=discord.Colour.red()
		)
		# embed.set_author(name='Anna Li stats')


		# I'm guessing that doing this operation kills the tz info
		# Therefore I'm leaving this in utc and later adding tz info
		# Basically keeping utc for any mongodb is good idea.
		today = datetime.datetime.utcnow()
		window = datetime.timedelta(days=-days)

		# Create window
		datetime_start = today + window
		datetime_end = today

		result = self.db.kakera_claimed.aggregate([
			{
				'$match': {
					'time': {
						'$gte': datetime_start,
						'$lt': datetime_end
					}
				}
			}, {
				'$group': {
					'_id': '$claimer',
					'value':{'$sum':"$value"},
					'kakeraP': {'$sum':{'$cond':[{'$eq':['kakeraP','$kakera']},1,0]}},
					'kakera': {'$sum':{'$cond':[{'$eq':['kakera','$kakera']},1,0]}},
					'kakeraT': {'$sum':{'$cond':[{'$eq':['kakeraT','$kakera']},1,0]}},
					'kakeraG': {'$sum':{'$cond':[{'$eq':['kakeraG','$kakera']},1,0]}},
					'kakeraY': {'$sum':{'$cond':[{'$eq':['kakeraY','$kakera']},1,0]}},
					'kakeraO': {'$sum':{'$cond':[{'$eq':['kakeraO','$kakera']},1,0]}},
					'kakeraR': {'$sum':{'$cond':[{'$eq':['kakeraR','$kakera']},1,0]}},
					'kakeraW': {'$sum':{'$cond':[{'$eq':['kakeraW','$kakera']},1,0]}}
				}
			}, {
				'$lookup': {
					'from': 'kakera_rolled',
					'localField': '_id',
					'foreignField': 'roller',
					'as': 'rolled'
				}
			}, {
				'$unwind':{'path':'$rolled'}
			}, {
				'$project': {
					'claimed': {
						'value': "$value",
						'kakeraP': '$kakeraP',
						'kakera': '$kakera',
						'kakeraT': '$kakeraT',
						'kakeraG': '$kakeraG',
						'kakeraY': '$kakeraY',
						'kakeraO': '$kakeraO',
						'kakeraR': '$kakeraR',
						'kakeraW': '$kakeraW'
					},
					'rolled': '$rolled'
				}
			}, {
				'$match': {
					'rolled.time': {
						'$gte': datetime_start,
						'$lt': datetime_end
					}
				}
			}, {
				'$group': {
					'_id': {'name': '$_id', 'claimed': '$claimed'},
					'kakeraP': {'$sum':{'$cond':[{'$eq':['kakeraP','$rolled.kakera']},1,0]}},
					'kakera': {'$sum':{'$cond':[{'$eq':['kakera','$rolled.kakera']},1,0]}},
					'kakeraT': {'$sum':{'$cond':[{'$eq':['kakeraT','$rolled.kakera']},1,0]}},
					'kakeraG': {'$sum':{'$cond':[{'$eq':['kakeraG','$rolled.kakera']},1,0]}},
					'kakeraY': {'$sum':{'$cond':[{'$eq':['kakeraY','$rolled.kakera']},1,0]}},
					'kakeraO': {'$sum':{'$cond':[{'$eq':['kakeraO','$rolled.kakera']},1,0]}},
					'kakeraR': {'$sum':{'$cond':[{'$eq':['kakeraR','$rolled.kakera']},1,0]}},
					'kakeraW': {'$sum':{'$cond':[{'$eq':['kakeraW','$rolled.kakera']},1,0]}}
				}
			}, {
				'$project': {
					'_id': 0,
					'name': '$_id.name',
					'claimed': '$_id.claimed',
					'rolled': {
						'kakeraP': '$kakeraP',
						'kakera': '$kakera',
						'kakeraT': '$kakeraT',
						'kakeraG': '$kakeraG',
						'kakeraY': '$kakeraY',
						'kakeraO': '$kakeraO',
						'kakeraR': '$kakeraR',
						'kakeraW': '$kakeraW'
					}
				}
			}, {
				'$addFields':{'value': "$claimed.value"}
			}, {
				'$project':{"claimed.value": 0}
			}, {
				'$sort':{'value': -1}
			}
		])

		# Format time
		time_format = "%m/%d %H:%M"
		window = utc_to_local(datetime_start).strftime(time_format) + " - " + utc_to_local(datetime_end).strftime(time_format)

		# Print the window
		embed.add_field(
			name="Anna Li stats",
			value=window,
			inline=False
		)

		# For each user
		for doc in result:

			# Unpack the values 
			name, value, rolled, claimed = doc['name'], doc['value'], doc['rolled'], doc['claimed']
			rolls 	= self.KAKERA_STATS_TEMPLATE % tuple(["**" + str(v) + "**" for v in rolled.values()])
			claims 	= self.KAKERA_STATS_TEMPLATE % tuple(["**" + str(v) + "**" for v in claimed.values()])
			kakera_count = sum(list(claimed.values())[1:])

			# Print their rolls and claims
			embed.add_field(
				# name="`" + "{:25}{:>10}{:>10,}".format(name, "Count:" + str(kakera_count), value) + "`",
				# value="Rolled: " + str(rolls) + '\n' + "Claims: " + str(claims),
				name="`" + "{:15}{:>10}{:>8,}".format(name, "Count:" + str(kakera_count), value) + "`",
				value="R: " + str(rolls) + '\n' + "C: " + str(claims),
				inline=False
			)

		# Report the time it took to compute this
		time_end = time.time()
		compute_time = "Time: " + str(round(time_end - time_start, 2)) + "s"
		# embed.set_footer(text="{:25}{:>8}".format(window, compute_time))
		embed.set_footer(text=compute_time)

		# Send the embed stats
		await ctx.send(embed=embed)

	@_stats.error
	async def _stats_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send(error)
		else:
			print(error)

	@commands.command(
		name='lock',
		aliases=['lock on this channel'],
		brief='Locks to channel with rolls',
		description='Must be done before rolls can be made',
		help='Set: to set to this channel\nReset: config defaults',
		usage='[set|reset]')
	async def _lock(self, ctx, reset='state'):

		# Lock on this channel only
		if reset == 'set':
			self.data['channel'] = ctx.channel.id

		if reset == 'reset':
			self.data['channel'] = config.STATS_TRACKER_CHANNEL_ID

		await ctx.send("Locked on: " + str(self.bot.get_channel(self.data['channel'])))

	@commands.command(
		name='snipe',
		aliases=['steal', 'snips', 'snip'],
		brief='Last 10 snips',
		description='Who sniped who?!',
		help='limit: the amount of recent snips to show',
		usage='limit')
	async def _snipe(self, ctx, limit=5):

		time_start = time.time()

		result = self.db.kakera_claimed.aggregate([
			{
				'$match': {'$expr': {'$ne': ['$roller', '$claimer']}}
			}, {
				'$sort': {'time': -1}
			}, {
				'$limit': limit
			}
		])

		# Make the embed
		embed = discord.Embed(
			colour=discord.Colour.green()
		)
		embed.set_author(name='Anna Li Snipes')

		# Print the window
		embed.add_field(
			name=str(limit) + " most recent",
			value="`{:<15}=> {:<15}`".format("Roller", "Claimer"),
			inline=False
		)

		time_format = "%m/%d %H:%M"

		# For each user
		for doc in result:

			# Unpack the values
			time_stamp, value, kakera, roller, claimer = doc['time'], doc['value'], doc['kakera'], doc['roller'], doc['claimer']

			# Convert timezone and format
			time_str = utc_to_local(time_stamp).strftime(time_format)

			# Print their rolls and claims
			embed.add_field(
				name="`{:<15}=> {:<15}`".format(roller, claimer),
				value= "{:<15} (**{:>6,}**) {}".format(self.MY_KAKERA_EMOTES[kakera], value, time_str),
				inline=False
			)

		# Report the time it took to compute this
		time_end = time.time()
		compute_time = "Time: " + str(round(time_end - time_start, 2)) + "s"
		embed.set_footer(text=compute_time)

		# Send the embed stats
		await ctx.send(embed=embed)

	@_snipe.error
	async def _snipe_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send(error)
		else:
			print(error)



# Give the cog to the bot
def setup(bot):
	bot.add_cog(TrackCog(bot))