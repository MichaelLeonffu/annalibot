# waifureader.py

# Reads in waifu data and saves it to the cloud for later use


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
# io
import io


# Our waifureader cog
class WaifureaderCog(commands.Cog, name="WaifureaderCog"):
	"""WaifureaderCog"""

	# Allows us to have bot defined and passed in
	def __init__(self, bot):
		self.bot = bot

		# Connect the mongodb client
		self.client = pymongo.MongoClient(config.DB_URI)
		self.db = self.client.waifu



	@commands.command(
		name='waifuread',
		aliases=['wr'],
		brief='Reads in waifus',
		description='Reads in waifus from file',
		help='Copy and paste all of the waifus using the "$mmrak-=i-s" command.\nDiscord will prompt to make it into a file, type "\%wr"')
	async def _waifuread(self, ctx):

		return await ctx.send("deprecated use wg")

		time_start = time.time()

		# Read in the file attachment
		if len(ctx.message.attachments) != 1:
			return await ctx.send("Wrong numebr of files")

		# Find the attachment
		attachment = ctx.message.attachments[0]

		# Check if attachment is bigger than 1MB
		if int(attachment.size) > 1048576:
			return await ctx.send("File is too big (>1MB)")

		# Read the file into a string called data and remove the white spaces
		data = [line for line in (await attachment.read()).decode().split('\n') if line != '']
		userid = int(ctx.message.author.id)

		# Go process the file string and upload the data to the database

		# Process all the data now that it is off the file
		waifuSeries = {}	# Must be dict to easy look up series name
		waifuList = []		# Array because we don't look up and all items unique
		series = ''
		for d in data:
			# Series

			print(d)

			# Check if this is a seies looking for the " - NN/NN\n"
			r = re.search(' - \d+\/\d+', d)

			# If it is a series
			if r:

				# Set the series
				series = re.split(' - \d+\/\d+',d)[0]

				# Get the value (where own/total)
				own, total = r.group()[3:].strip().split('/')

				# Add this series to the list (include own and total info)
				waifuSeries[series] = {
					'_id': series,		# This helps latter when formatting again
					'owner': userid,	# The user that owns this character
					'own': int(own),
					'total': int(total),
					'characters': []
				}
				
			# Character
			else:

				# Split the three components (strip the \n)
				comp = re.split(' - ', d.strip())

				# Note: customs don't have likes
				if len(comp) == 2:
					likes = '#0'
					nameValue, pic = comp
				else:
					likes, nameValue, pic = comp
				# Don't worry about bad input data

				# Matches the group
				valueKa = re.search(' \d+ ka$', nameValue)
				# Separates the " 123 ka"
				value = valueKa.group().strip()[:-3]

				# Extracts the name from the remainder
				name = re.sub(' \d+ ka$', '', nameValue).strip()

				# For the given series, add a entry with the name
				waifuSeries[series]['characters'].append(name)		# This is also the _id

				waifuList.append(
					{
						'_id': name,				# Unique id per mudae
						'owner': userid,			# The user that owns this character	
						'series': series,			# So it can refer to its series
						'likes': int(likes[1:]),	# The number of likes
						'value': int(value),		# The value it has (kakera)
						'pic': pic					# url for the pic of it
					}
				)


		# First must convert into an array
		waifuSeries_insert = [seriesName[1] for seriesName in waifuSeries.items()]

		pprint.pprint(waifuSeries_insert)
		pprint.pprint(waifuList)

		# Insert it into the database (change this to upsert many)
		self.db.waifuSeries.insert_many(waifuSeries_insert)
		self.db.waifuList.insert_many(waifuList)

		# Report the time it took to compute this
		time_end = time.time()
		compute_time = "Time: " + str(round(time_end - time_start, 2)) + "s"

		# Completed
		return await ctx.send("Done, " + compute_time)

	@_waifuread.error
	async def _waifuread_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send(error)
		else:
			await ctx.send(error)


	@commands.command(
		name='waifuprint',
		aliases=['wp'],
		brief='Print out waifus',
		description='Print out waifus',
		help='Generates a html file for printing the waifus')
	async def _waifuprint(self, ctx, limit=100):

		return await ctx.send("deprecated use wg")

		time_start = time.time()

		# Read from the sender
		user = ctx.author
		# If there is a mentions use that user
		if len(ctx.message.mentions) >= 1:
			user = ctx.message.mentions[0]

		# The main structure which contains all the pics
		html_template = """ <!DOCTYPE html>
		<html>
			<head>
				<style>
					* {{box-sizing: border-box;}}

					.container {{
						position: relative;
						/*width: 50%;*/
						max-width: 225px;
					}}

					.image {{
						display: block;
						width: 100%;
						height: auto;
					}}

					.overlay {{
						position: absolute; 
						bottom: 0; 
						background: rgb(0, 0, 0);
						background: rgba(0, 0, 0, 0.5); /* Black see-through */
						color: #f1f1f1; 
						width: 100%;
						transition: .5s ease;
						opacity:0;
						color: white;
						font-size: 20px;
						padding: 20px;
						text-align: center;
					}}

					.container:hover .overlay {{
						opacity: 1;
					}}

					div {{
						float: left;
						width: 50%;
						height: 25%;
					}}
				</style>
				<title>Waifu List</title>
			</head>
			<body>

				<h1>{0}'s Waifu list</h1>
				<!-- <p>This is a paragraph.</p> -->

				{1}

			</body>
		</html> """

		# For the aggregation framework
		pipeline = [
			{
				'$match': {'owner': int(user.id)}
			}, {
		        '$lookup': {
		            'from': 'waifuList', 
		            'localField': 'characters', 
		            'foreignField': '_id', 
		            'as': 'characters'
		        }
		    }, {
		        '$addFields': {
		            'like': {
		                '$min': '$characters.likes'
		            }
		        }
		    }, {
		        '$unwind': {
		            'path': '$characters'
		        }
		    }, {
		        '$project': {
		            '_id': 0, 
		            'name': '$characters._id', 
		            'series_like': '$like', 
		            'character_like': '$characters.likes', 
		            'pic': '$characters.pic', 
		            'comp_like': {
		                '$add': [
		                    {
		                        '$multiply': [
		                            100000, '$like'
		                        ]
		                    }, '$characters.likes'
		                ]
		            }
		        }
		    }, {
		        '$sort': {
		            'comp_like': 1
		        }
		    }
		]

		# Do the aggregation
		# waifu_order = list(self.db.waifuSeries.aggregate(pipeline))

		# Do a basic search
		waifu_order = self.db.waifuList.find({'owner': int(user.id)}, {'_id': 1, 'likes': 1, 'pic': 1}).sort('likes', 1)[:limit]

		# Fits in the template
		pic_html_template = '<img src="{0}" alt="{1}" style="width:225px;height:350px;">'

		pic_html_template = """
		<div class="container">
			<img src="{0}" alt="{1}" style="width:225px;height:350px;" class="image">
			<div class="overlay">{1} #{2}</div>
		</div>
		"""

		# List of all the populated pic html templates
		# pics_html = [pic_html_template.format('./pics/' + pic, pic) for pic in pics]
		# pics_html = [pic_html_template.format(waifu['pic'], waifu['name']) for waifu  in waifu_order]
		pics_html = [pic_html_template.format(waifu['pic'], waifu['_id'], waifu['likes']) for waifu in waifu_order]

		# Join all the pics together and then place it in the main template
		html_file = html_template.format(user.name, "".join(pics_html))

		# Convert the string into bytes so it can be made into a file
		html_bytes = bytes(html_file, 'utf8')

		# From bytes we need to get it into a file like object using io.BytesIO
		html_buffer = io.BytesIO()
		html_buffer.write(html_bytes)

		# Reset the reading to the start
		html_buffer.seek(0)

		# Report the time it took to compute this
		time_end = time.time()
		compute_time = "Time: " + str(round(time_end - time_start, 2)) + "s"

		# Completed
		return await ctx.send("Done, " + compute_time, file=discord.File(html_buffer, filename='waifulist.html'))

	@_waifuprint.error
	async def _waifuprint_error(self, ctx, error):
		await ctx.send(error)

	@commands.command(
		name='waifugenerate',
		aliases=['wg'],
		brief='Reads in waifus and writes waifus',
		description='Reads a waifu file then writes a html',
		help='Copy and paste all of the waifus using the "$mmk-=i-s" command.\nDiscord will prompt to make it into a file, type "\%wr"')
	async def _waifugenerate(self, ctx, name=None):

		time_start = time.time()

		# Read in the file attachment
		if len(ctx.message.attachments) != 1:
			return await ctx.send("Wrong numebr of files")

		# Find the attachment
		attachment = ctx.message.attachments[0]

		# Check if attachment is bigger than 1MB
		if int(attachment.size) > 1048576:
			return await ctx.send("File is too big (>1MB)")

		# Read the file into a string called data and remove the white spaces
		data = [line for line in (await attachment.read()).decode().split('\n') if line != '']
		userid = int(ctx.message.author.id)

		# Go process the file string and upload the data to the database

		# Process all the data now that it is off the file
		waifuList = []		# Array because we don't look up and all items unique
		line = 0
		for d in data:
			# Character
			line += 1

			# Split the three components (strip the \n)
			comp = re.split(' - ', d.strip())

			# Note: customs don't have likes
			if len(comp) == 2:
				likes = '#0'
				nameValue, pic = comp
			else:
				try:
					likes, nameValue, pic = comp
				except:
					return await ctx.send("Bad format! around line: " + str(line))
			# Don't worry about bad input data

			# Matches the group
			valueKa = re.search(' \d+ ka$', nameValue)
			# Separates the " 123 ka"
			value = valueKa.group().strip()[:-3]

			# Extracts the name from the remainder
			name = re.sub(' \d+ ka$', '', nameValue).strip()

			waifuList.append(
				{
					'_id': name,				# Unique id per mudae
					'owner': userid,			# The user that owns this character
					'likes': int(likes[1:]),  	# The number of likes
					'value': int(value),		# The value it has (kakera)
					'pic': pic					# url for the pic of it
				}
			)

		pprint.pprint(waifuList)

		# Read from the sender
		user = ctx.author
		# If there is a mentions use that user
		if len(ctx.message.mentions) >= 1:
			user = ctx.message.mentions[0]

		if name == None:
			name = user.name

		# The main structure which contains all the pics
		html_template = """ <!DOCTYPE html>
		<html>
			<head>
				<style>
					* {{box-sizing: border-box;}}

					.container {{
						position: relative;
						/*width: 50%;*/
						max-width: 225px;
					}}

					.image {{
						display: block;
						width: 100%;
						height: auto;
					}}

					.overlay {{
						position: absolute; 
						bottom: 0; 
						background: rgb(0, 0, 0);
						background: rgba(0, 0, 0, 0.5); /* Black see-through */
						color: #f1f1f1; 
						width: 100%;
						transition: .5s ease;
						opacity:0;
						color: white;
						font-size: 20px;
						padding: 20px;
						text-align: center;
					}}

					.container:hover .overlay {{
						opacity: 1;
					}}

					div {{
						float: left;
						width: 50%;
						height: 25%;
					}}
				</style>
				<title>Waifu List</title>
			</head>
			<body>

				<h1>{0}'s Waifu list</h1>
				<!-- <p>This is a paragraph.</p> -->

				{1}

			</body>
		</html> """


		# Fits in the template
		pic_html_template = '<img src="{0}" alt="{1}" style="width:225px;height:350px;">'

		pic_html_template = """
		<div class="container">
			<img src="{0}" alt="{1}" style="width:225px;height:350px;" class="image">
			<div class="overlay">{1} #{2}</div>
		</div>
		"""

		# List of all the populated pic html templates
		# pics_html = [pic_html_template.format('./pics/' + pic, pic) for pic in pics]
		# pics_html = [pic_html_template.format(waifu['pic'], waifu['name']) for waifu  in waifu_order]
		pics_html = [pic_html_template.format(
			waifu['pic'], waifu['_id'], waifu['likes']) for waifu in waifuList]

		# Join all the pics together and then place it in the main template
		html_file = html_template.format(name, "".join(pics_html))

		# Convert the string into bytes so it can be made into a file
		html_bytes = bytes(html_file, 'utf8')

		# From bytes we need to get it into a file like object using io.BytesIO
		html_buffer = io.BytesIO()
		html_buffer.write(html_bytes)

		# Reset the reading to the start
		html_buffer.seek(0)

		# Report the time it took to compute this
		time_end = time.time()
		compute_time = "Time: " + str(round(time_end - time_start, 2)) + "s"

		# Completed
		return await ctx.send("Done, " + compute_time, file=discord.File(html_buffer, filename=(user.name+".html")))

	@_waifuprint.error
	async def _waifuprint_error(self, ctx, error):
		await ctx.send(error)



# Give the cog to the bot
def setup(bot):
	bot.add_cog(WaifureaderCog(bot))
