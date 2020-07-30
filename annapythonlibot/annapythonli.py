# annapythonli.py

# Config
from config.config import DISCORD_TOKEN
# This is the discord
import discord
from discord.ext import commands
# Pretty print
# import pprint
# # regex
# import re


# The client
# client = discord.Client()
client = commands.Bot(
	command_prefix	= ('^','%'),
	activity		= discord.Game(name="with fire")
)

# Commands
@client.command()
async def test(ctx, *args):
	await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))

@client.command(name='add')
async def _add(ctx, a: int, b: int):
	await ctx.send(a + b)

@_add.error
async def _add_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send(error)

# @client.command(name='eval')
# @commands.is_owner()
# async def _eval(ctx, *, code):
# 	"""A bad example of an eval command"""
# 	await ctx.send(eval(code))


# Handles events (functions that take care of events that happen)

@client.event
# When the bot connects to discord
async def on_ready():
	print(f'{client.user} has connected to Discord!')



# @client.event
# # When the bot gets a message
# async def on_message(message):

# 	# BASICS

# 	# If the bot is reading it's own message
# 	if message.author == client.user:
# 		return

# 	# Lock on this channel only
# 	if message.content == "lock on this channel":
# 		client.my_channel = message.channel
# 		await message.channel.send("Locked on: " + str(client.my_channel))
# 		return

# 	# The block
# 	if message.channel != client.my_channel:
# 		return


# 	# :kakeraT:

# 	if len(message.embeds) > 0:
# 		pprint.pprint(message.embeds[0].to_dict()['description'])
	

# 	# CORE


# 	# Keep track of the person that sent the last command
# 	if message.content.lower() in client.my_ROLL_COMMANDS:
# 		client.my_last_user = message.author.name
# 		return


# 	# print(message.author, message.content, message.reactions)
# 	# Mudamaid 18#0442 <:kakeraY:605124267574558720>**Larypie +406** ($k) []

# 	# Count when the kakera was collected
# 	if message.content in client.my_ROLL_COMMANDS:
# 		# Knowing that the bot will react with kakera
# 		return

# 	# Count when the kakera was collected
# 	if message.content.find("($k)") > 0 and message.content.find("kakera") > 0:

# 		# Figureout which kakera it was
# 		kakera_type = ""
# 		for parts in message.content.split(":"):
# 			if "kakera" in parts:
# 				kakera_type = parts

# 		# If there is no data for that user then make an empty data sheet
# 		if client.my_last_user not in client.my_data:
# 			client.my_data[client.my_last_user] = {field: client.my_TEMPLATE_KAK_TYPE.copy() for field in "rolled claimed".split()}

# 		# Update the data on that user
# 		client.my_data[client.my_last_user]['claimed'][kakera_type] += 1
# 		print("Added Claim")
# 		await message.channel.send("you claimed!")
# 		return


# 	# Output the running data
# 	if message.content == "Anna Li stats":
# 		print(client.my_data)
# 		await message.channel.send(client.my_data)
# 		return


# 	# MISC

# 	# If the message is add Nina it will add nina
# 	if message.content == "add Nina":
# 		client.my_nina += 1
# 		await message.channel.send("There is: " + str(client.my_nina))
# 		return

# 	# If the message is what we expect then reply to it
# 	if message.content == "Anna Li":
# 		await message.channel.send("pog")
# 		return


# @client.event
# # When the bot notices a reaction to a message
# async def on_reaction_add(reaction, user):

# 	message = reaction.message

# 	# BASICS

# 	# If the bot is reading it's own message
# 	if message.author == client.user:
# 		return

# 	# The block (Lock set up in the messages events)
# 	if message.channel != client.my_channel:
# 		return
	

# 	# CORE


# 	# What  does kakera reaction look like in str form
# 	# print(str(reaction))

# 	# Count who rolled the kakera
# 	if str(reaction) in client.my_KAKERA_REACT_TYPES:

# 		# Extract out the thing in between the :
# 		for part in str(reaction).split(":"):
# 			if part in client.my_KAKERA_TYPES:
# 				kakera = part

# 		# If there is no data for that user then make an empty data sheet
# 		if client.my_last_user not in client.my_data:
# 			client.my_data[client.my_last_user] = {field: client.my_TEMPLATE_KAK_TYPE.copy() for field in "rolled claimed".split()}

# 		# Update the data on that user
# 		client.my_data[client.my_last_user]['rolled'][kakera] += 1
# 		print("Added")
# 		return


# 	# MISC

# 	# If the message is what we expect then reply to it
# 	if message.content == "React":
# 		await message.channel.send(reaction)
# 		return

# Connect the client to discord
client.run(DISCORD_TOKEN)
