# annapythonli.py

# Config
from config.config import DISCORD_TOKEN
# This is the discord
import discord
from discord.ext import commands
# Pretty print
# import pprint
# Regex
# import re
# Time
import time
# Context
import contextvars as ctxvar
# Async
import asyncio


# Time keeping
time_start_var = ctxvar.ContextVar('time_start')
time_start_var.set(time.time())

def time_pretty(dTime):
	hours, remainder = divmod(dTime, 3600)
	minutes, seconds = divmod(remainder, 60)
	return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))



# The client
# client = discord.Client()
# The bot
bot = commands.Bot(
	command_prefix	= ('!', '%', 'a!', 'annali!', 'annali'),
	activity		= discord.Game(name="with fire")
)

# Commands
@bot.command()
async def test(ctx, *args, hidden=True):
	await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))

@bot.command(
	name='time',
	aliases=['t'],
	brief='How long Anna Li has been running',
	description='The amount of time hr:min:sec Anna Li has been running',
	help='(More like the amount of time Anna Li bot has not been updated',
	usage='%time')
async def _time(ctx):
	await ctx.send(time_pretty(time.time() - time_start_var.get()))

@bot.command(
	name='add',
	aliases=['a'],
	brief='Adds two numbers',
	description='So I\' hear that you wana add two numbers ;)',
	help='Well, with the `add` command you can do just that!',
	usage='%add(int a, int b)')
async def _add(ctx, a: int, b: int):
	await ctx.send(a + b)

@bot.command(
	name='mul',
	aliases=['m'],
	brief='Mulitplies two numbers',
	description='So I\' hear that you wana multiply two numbers ;)',
	help='Well, with the `mul` command you can do just that!',
	usage='%mul(int a, int b)')
async def _mul(ctx, a: int, b: int):
	await ctx.send(a * b)

@_add.error
async def _add_error(ctx, error):
	if isinstance(error, commands.BadArgument):
		await ctx.send(error)

# @bot.command(name='eval')
# @commands.is_owner()
# async def _eval(ctx, *, code):
# 	"""A bad example of an eval command"""
# 	await ctx.send(eval(code))


# Handles events (functions that take care of events that happen)

@bot.event
# When the bot connects to discord
async def on_ready():
	print(f'{bot.user} has connected to Discord!')


@bot.command()
async def pages(ctx):
    contents = ["This is page 1!", "This is page 2!", "This is page 3!", "This is page 4!"]
    pages = 4
    cur_page = 1
    message = await ctx.send(f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
    # getting the message object for editing and reacting

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
        # This makes sure nobody except the command sender can interact with the "menu"

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)
            # waiting for a reaction to be added - times out after x seconds, 60 in this
            # example

            if str(reaction.emoji) == "▶️" and cur_page != pages:
                cur_page += 1
                await message.edit(content=f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                cur_page -= 1
                await message.edit(content=f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
                await message.remove_reaction(reaction, user)

            else:
                await message.remove_reaction(reaction, user)
                # removes reactions if the user tries to go forward on the last page or
                # backwards on the first page
        except asyncio.TimeoutError:
            await message.delete()
            break
            # ending the loop if user doesn't react after x seconds


# # HELP

# # Remove the default help (here by default)
# bot.remove_command('help')

# # Add custom help command


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
bot.run(DISCORD_TOKEN)
