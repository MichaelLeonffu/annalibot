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
# pprint
import pprint


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
		if message.channel.id != self.data['channel']:
			return


		# Keep track of the person that sent the last command
		if message.content.lower() in self.ROLL_COMMANDS:
			# self.data['last_user'] = message.author.id
			self.data['last_user'] = message.author.name
			return

		# Check if the message has a embed in it (checking for gold +kakeras)
		if len(message.embeds) == 1:

			# Check if that message has a kakera gain
			kakera_gold_key = re.search(r'\*\*\+(\d+)\*\*<:kakera:469835869059153940>', ''.join(message.embeds[0].to_dict()['description']))

			# If there was a real kakera gain then count it
			if kakera_gold_key:

				# Extract the kakera value from what the key was worth
				kakera_value = kakera_gold_key.group(1)

				# There are always name in the footer if it was a authentic gold key rolled
				# name = message.embeds[0].to_dict()['footer']['text'][len('Belongs to '):]
				# Fails at "LEFT :warning: Belongs to Larypie"

				# Roller is always the one that married the character
				name = self.data['last_user']

				await message.channel.send(name + " you got: " + str(kakera_value))

				# Prepare doc
				doc = {
					'time': 	datetime.datetime.utcnow(),
					'claimer':	name,
					'value': 	int(kakera_value)
				}

				# Upload data to server
				self.db.kakera_gold_key.insert_one(doc)
				return


		# pprint.pprint(message.embeds[0].to_dict()['description'])
		# print(message.author, message.content, message.reactions)
		# Mudamaid 18#0442 <:kakeraY:605124267574558720>**Larypie +406** ($k) []

		kakera_collect = re.search(r'(<:kakera[PTGYORW]?:\d+>)(\(Free\) )?\*\*(.+) \+(\d+)\*\* \(\$k\)', message.content)

		# Count when the kakera was collected
		if kakera_collect:

			# Figureout which kakera it was; convert from full name to name
			kakera_type = kakera_collect.group(1)
			kakera_type = re.search(r'<:(kakera[PTGYORW]?):\d+>', kakera_type).group(1)

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
		if message.channel.id != self.data['channel']:
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

			# Also check if this character is in the 10 key alert and who wants that alert
			result = self.db.alert10.find_one({
				'character': message.embeds[0].to_dict()['author']['name'].lower()
			})

			# If there is a result then mention the user
			if result != None:
				await message.channel.send("10 Key {}: {}".format(self.MY_KAKERA_EMOTES[kakera_reaction.group(1)], self.bot.get_user(result['owner']).mention))

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


	@commands.command(
		name='stats',
		aliases=['s'],
		brief='Kakera stas',
		description='Reports the kakera roll and claim stats!',
		help='days (int): how many days back to search\nhours (int): how many hours back to search')
	async def _stats(self, ctx, days=1, hours=0):

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
		window = datetime.timedelta(days=-days, hours=-hours)

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
			value=window + " @" + str(hours+24*days) + " hours",
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
		name='flex_dat_gold',
		aliases=['flex dat', 'flex', 'dat', 'gold'],
		brief='Gold key kakera stas',
		description='Reports the kakera from gold key rolls!',
		help='days (int): how many days back to search\nhours (int): how many hours back to search')
	async def _flex_dat_gold(self, ctx, days=1, hours=0):

		time_start = time.time()

		# Make the embed
		embed = discord.Embed(
			colour=discord.Colour.gold()
		)
		# embed.set_author(name='Anna Li stats')


		# I'm guessing that doing this operation kills the tz info
		# Therefore I'm leaving this in utc and later adding tz info
		# Basically keeping utc for any mongodb is good idea.
		today = datetime.datetime.utcnow()
		window = datetime.timedelta(days=-days, hours=-hours)

		# Create window
		datetime_start = today + window
		datetime_end = today

		result = self.db.kakera_gold_key.aggregate([
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
					'count':{'$sum':1}
				}
			}, {
				'$sort':{'value': -1}
			}
		])

		# Format time
		time_format = "%m/%d %H:%M"
		window = utc_to_local(datetime_start).strftime(time_format) + " - " + utc_to_local(datetime_end).strftime(time_format)

		# Print the window
		embed.add_field(
			name="Anna Li Gold key stats",
			value=window + " @" + str(hours+24*days) + " hours",
			inline=False
		)

		# For each user
		for doc in result:

			# Unpack the values
			name, value, count = doc['_id'], doc['value'], doc['count']

			# Print their rolls and claims
			embed.add_field(
				name= name,
				value="`{:10}{:>8,}`".format("Count:" + str(count), value),
				inline=False
			)

		# Report the time it took to compute this
		time_end = time.time()
		compute_time = "Time: " + str(round(time_end - time_start, 2)) + "s"
		embed.set_footer(text=compute_time)

		# Send the embed stats
		await ctx.send(embed=embed)

	@_flex_dat_gold.error
	async def _flex_dat_gold_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send(error)
		else:
			print(error)


	@commands.command(
		name='lock',
		aliases=['lock on this channel'],
		brief='Locks to channel with rolls',
		description='Must be done before rolls can be made',
		help='Set: to set to this channel\nReset: config defaults')
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
		brief='Last 5 snips',
		description='Who sniped who?!',
		help='limit: the amount of recent snips to show')
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


	@commands.command(
		name='snipe_table',
		aliases=['snipe table', 'st'],
		brief='Day worth of snipes',
		description='Who sniped who?!',
		help='sniped (str): user name of sniped\ndays (int): how many days back to search\nhours (int): how many hours back to search')
	async def _snipe_table(self, ctx, sniped, days=1, hours=0):

		kakera_filter = ['kakeraP', 'kakeraO', 'kakeraR', 'kakeraW']

		time_start = time.time()

		# I'm guessing that doing this operation kills the tz info
		# Therefore I'm leaving this in utc and later adding tz info
		# Basically keeping utc for any mongodb is good idea.
		today = datetime.datetime.utcnow()
		window = datetime.timedelta(days=-days, hours=-hours)

		# Create window
		datetime_start = today + window
		datetime_end = today

		# Finding all results of snipes related to sniped
		result = self.db.kakera_claimed.aggregate([
			{
				'$match': {
					'time': {
						'$gte': datetime_start,
						'$lt': datetime_end
					},
					'kakera': { '$in': kakera_filter}
				}
		    }, {
		        '$match': {
		            '$expr': {
		                '$or': [
		                    {
		                        '$eq': [
		                            '$roller', str(sniped)
		                        ]
		                    }, {
		                        '$eq': [
		                            '$claimer', str(sniped)
		                        ]
		                    }
		                ]
		            }
		        }
		    }, {
		        '$match': {
		            '$expr': {
		                '$ne': [
		                    '$roller', '$claimer'
		                ]
		            }
		        }
		    }, {
		        '$group': {
		            '_id': {
		                'roller': '$roller',
		                'claimer': '$claimer',
		                'kakera': '$kakera'
		            },
		            'value': {
		                '$sum': '$value'
		            },
		            'count': {
		                '$sum': 1
		            }
		        }
		    }, {
		        '$group': {
		            '_id': {
		                'roller': '$_id.roller',
		                'claimer': '$_id.claimer'
		            },
		            'value': {
		                '$sum': '$value'
		            },
		            'kakera': {
		                '$push': {
		                    'k': '$_id.kakera',
		                    'v': {
		                        'value': '$value',
		                        'count': '$count'
		                    }
		                }
		            }
		        }
		    }, {
		        '$project': {
		            '_id': 0,
		            'roller': '$_id.roller',
		            'claimer': '$_id.claimer',
		            'value': 1,
		            'kakera': {
		                '$arrayToObject': '$kakera'
		            }
		        }
		    }, {
		        '$sort': {
		            'value': -1
		        }
		    }, {
		        '$facet': {
		            'sniped': [
		                {
		                    '$match': {
		                        '$expr': {
		                            '$eq': [
		                                '$roller', str(sniped)
		                            ]
		                        }
		                    }
		                }
		            ],
		            'sniper': [
		                {
		                    '$match': {
		                        '$expr': {
		                            '$eq': [
		                                '$claimer', str(sniped)
		                            ]
		                        }
		                    }
		                }
		            ]
		        }
		    }
		])

		# Make the embed
		embed = discord.Embed(
			colour=discord.Colour.purple()
		)
		# embed.set_author(name='Anna Li Snipe Table')

		time_format = "%m/%d %H:%M"
		window = utc_to_local(datetime_start).strftime(time_format) + " - " + utc_to_local(datetime_end).strftime(time_format)

		# Print the window
		embed.add_field(
			name="Anna Li Snipe table",
			value=window + " @" + str(hours+24*days) + " hours",
			inline=False
		)

		# Only one doc should be resulted
		oneResult = list(result)[0]

		# Print the window
		embed.add_field(
			name="You are the Sniper: " + sniped,
			value="You've sniped:",
			inline=False
		)

		# Generate the sniper data first (for each sniper) sniper = claimer = us;
		for doc in oneResult['sniper']:

			# Unpack the values
			value, kakeras, roller, claimer = doc['value'], doc['kakera'], doc['roller'], doc['claimer']


			# Format kakeras to be a list in order
			kakera_formated = []

			# For each of the kakera
			for kname in kakera_filter:

				# For each of them by name
				if kname in kakeras:
					kakera_formated.append({'kakera': kname, 'value': kakeras[kname]['value'], 'count': kakeras[kname]['count']})
				else:
					kakera_formated.append({'kakera': kname, 'value': 0, 'count': 0})

			kakera_list = ' '.join(["**" + str(k['count']) + "**" + self.MY_KAKERA_EMOTES[k['kakera']] for k in kakera_formated])

			embed.add_field(
				name="`" + "{:15} {:>10}{:>8,}".format(roller, "Count:" + str("#?"), value) + "`",
				# name="`{:<15}=> {:<15}: {}`".format(roller, claimer, value),
				# value= "{:<15} {}(**{:>6,}**) {}".format(self.MY_KAKERA_EMOTES[kname], kakeras[kname]['count'], kakeras[kname]['value'], "lol"),
				value=kakera_list,
				inline=False
			)

		# Print the window
		embed.add_field(
			name="You are the Sniped: " + sniped,
			value="You've been Sniped by:",
			inline=False
		)

		# Generate the sniped data first (for each sniped) sniped = roller = us;
		for doc in oneResult['sniped']:

			# Unpack the values
			value, kakeras, roller, claimer = doc['value'], doc['kakera'], doc['roller'], doc['claimer']


			# Format kakeras to be a list in order
			kakera_formated = []

			# For each of the kakera
			for kname in kakera_filter:

				# For each of them by name
				if kname in kakeras:
					kakera_formated.append({'kakera': kname, 'value': kakeras[kname]['value'], 'count': kakeras[kname]['count']})
				else:
					kakera_formated.append({'kakera': kname, 'value': 0, 'count': 0})

			kakera_list = ' '.join(["**" + str(k['count']) + "**" + self.MY_KAKERA_EMOTES[k['kakera']] for k in kakera_formated])

			embed.add_field(
				name="`" + "{:15} {:>10}{:>8,}".format(claimer, "Count:" + str("#?"), value) + "`",
				# name="`{:<15}=> {:<15}: {}`".format(roller, claimer, value),
				# value= "{:<15} {}(**{:>6,}**) {}".format(self.MY_KAKERA_EMOTES[kname], kakeras[kname]['count'], kakeras[kname]['value'], "lol"),
				value=kakera_list,
				inline=False
			)


		# Report the time it took to compute this
		time_end = time.time()
		compute_time = "Time: " + str(round(time_end - time_start, 2)) + "s"
		embed.set_footer(text=compute_time)

		# Send the embed stats
		await ctx.send(embed=embed)

	# @_snipe_table.error
	# async def _snipe_table_error(self, ctx, error):
	# 	if isinstance(error, commands.BadArgument):
	# 		await ctx.send(error)
	# 	if isinstance(error, commands.MissingRequiredArgument):
	# 		await ctx.send(error)
	# 	else:
	# 		print(error)

	@commands.command(
		name='alert',
		aliases=['alrt'],
		brief='10 Key alert',
		description='Mentions user that has set the alert for this character',
		help='Mentions the user that set the alert')
	async def _alert(self, ctx, *arg):

		# Input parsing
		characters = ' '.join(arg).split('$')

		# Input doc for each character per this user
		if len(characters) > 0:

			# Prepare docs
			docs = [{
				'owner': 		ctx.author.id,
				'character': 	character.strip().lower()
			} for character in characters]

			# Upload data to server
			self.db.alert10.insert_many(docs)

			return await ctx.send("Added {} characters to alert".format(len(characters)))

		await ctx.send("Failed to add characters")

	# @_alert.error
	# async def _alert(self, ctx, error):
	# 	if isinstance(error, commands.BadArgument):
	# 		await ctx.send(error)
	# 	else:
	# 		print(error)

	@commands.command(
		name='unalert',
		aliases=['ua'],
		brief='10 Key unalert',
		description='Removes an alert',
		help='In the case you do not want to be alerted anymore')
	async def _unalert(self, ctx, *arg):

		# Input parsing
		characters = ' '.join(arg).split('$')

		# Input doc for each character per this user
		if len(characters) > 0:

			# Prepare docs
			docs = [{
				'owner': 		ctx.author.id,
				'character': 	character.strip().lower()
			} for character in characters]

			for doc in docs:

				# Delete one data from server
				result = self.db.alert10.delete_one(doc)

				if result.deleted_count != 1:
					await ctx.send("Failed to unalert **{}** from alert".format(doc['character']))

			return await ctx.send("Processed **{}** characters".format(len(characters)))

		await ctx.send("Failed to remove characters")

	# @_unalert.error
	# async def _unalert_error(self, ctx, error):
	# 	if isinstance(error, commands.BadArgument):
	# 		await ctx.send(error)
	# 	else:
	# 		print(error)

	@commands.command(
		name='alert_list',
		aliases=['al'],
		brief='10 Key alert list',
		description='Mentions user that has set the alert for this character',
		help='Mentions the user that set the alert')
	async def alert_list(self, ctx):

		# Select the user to read from

		# Read from the sender
		user = ctx.author
		# If there is a mentions use that user
		if len(ctx.message.mentions) >= 1:
			user = ctx.message.mentions[0]

		# Gather all the characters in alert for this person
		results = self.db.alert10.find({
			'owner': user.id
		})

		# Generate it into an array
		characters = [result['character'] for result in list(results)]

		# Message to send limited to 2000 characters
		message = ""
		for character in characters:
			if len(message) + len(character) + 5 > 2000:

				# Send these characters first
				await ctx.send(message)
				message = ""

			message += ", " + character 

		# Send the embed stats
		await ctx.send(message)

	# @alert_list.error
	# async def alert_list(self, ctx, error):
	# 	if isinstance(error, commands.BadArgument):
	# 		await ctx.send(error)
	# 	else:
	# 		print(error)


# Give the cog to the bot
def setup(bot):
	bot.add_cog(TrackCog(bot))