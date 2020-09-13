# misc.py

# Just some random commands (loose ends)


# This is the discord
import discord
from discord.ext import commands
# Regex
import re
# AsyncIo
import asyncio


# Our simple cog
class MiscCog(commands.Cog, name="Misc Commands"):
	"""MiscCog"""

	# Allows us to have bot defined and passed in
	def __init__(self, bot):
		self.bot = bot



	# @commands.command(
	# 	name='math',
	# 	aliases=['m'],
	# 	brief='Does math',
	# 	description='So Anna Li can do math, what can you do?',
	# 	help='Anna Li can do your math! (Supported + - * /)',
	# 	rest_is_raw=True)
	# async def _math(self, ctx, *args):

	# 	# Remove all the space and join together
	# 	args = ''.join(args)

	# 	# Separating between numbers and operators
	# 	acc = ""
	# 	infix = []
	# 	for arg in args:
	# 		if arg.isnumeric():
	# 			acc += arg
	# 		else:
	# 			infix.append(acc)
	# 			infix.append(arg)
	# 			acc = ""

	# 	# This is likely given in infix notation
	# 	operator_stack, operand_stack = [], []

	# 	# Valid operators currently
	# 	operators = "- + / * ( )".split(' ')

	# 	# Precedence rules PEMDAS
	# 	precedence_rules = {op: operators.index(op) for op in operators}

	# 	# Algorithm
	# 	for arg in infix:
	# 		if arg in operators:			# Operator
	# 			while precedence_rules[operator_stack[-1:]] >= arg:
	# 				top_op = operator_stack.pop()
	# 				op1, op2 = operand_stack.pop(), operand_stack.pop()
	# 				operand_stack.append(eval("op1 top_op op2"))

	# 		else:							# Operand
	# 			# If it is not a valid operand then stop
	# 			if not arg.isnumeric():
	# 				return await ctx.send("Invalid operand: {}".format(arg))
	# 			operand_stack.append(arg)

	# 	await ctx.send(arg)


	@commands.command(
		name='mypic',
		# aliases=['mypic'],
		brief='Show this profile pic',
		description='You wana see yourself?',
		help='Lets get that for you')
	async def _mypic(self, ctx, size=1024):
		await ctx.send(ctx.author.avatar_url_as(size=size))


	@commands.command(
		name='yourpic',
		# aliases=['yourpic'],
		brief='Show your profile pic',
		description='You wana see someone else?',
		help='Lets get that for you')
	async def _myourpic(self, ctx, mention, size=1024):
		await ctx.send((await commands.MemberConverter().convert(ctx, mention)).avatar_url_as(size=size))


	@commands.command(
		name='add',
		aliases=['sum'],
		brief='Adds one or more numbers',
		description='So I\' hear that you wana add one or more numbers ;)',
		help='Well, with the `add` command you can do just that!')
	async def _add(self, ctx, *nums: float):
		if len(nums) < 1: await ctx.send("Requires at least one number")
		await ctx.send(sum(nums))


	@commands.command(
		name='mul',
		aliases=['multiply'],
		brief='Mulitplies one or more numbers',
		description='So I\' hear that you wana multiply one or more numbers ;)',
		help='Well, with the `mul` command you can do just that!')
	async def _mul(self, ctx, *nums: float):
		if len(nums) < 1: await ctx.send("Requires at least one number")
		total = 1
		for num in nums:
			total *= num
		await ctx.send(total)


	@commands.command(
		name='div',
		aliases=['divide'],
		brief='Divide one or more numbers',
		description='So I\' hear that you wana divide one or more numbers ;)',
		help='Well, with the `divide` command you can do just that!')
	async def _div(self, ctx, *nums: float):
		if len(nums) < 1: await ctx.send("Requires at least one number")
		nums = list(nums)
		nums.reverse()
		total = nums.pop()
		while len(nums) > 0:
			total /= nums.pop()
		await ctx.send(total)

	@_mypic.error
	@_myourpic.error
	@_div.error
	@_mul.error
	@_add.error
	async def _any_error(self, ctx, error):
		await ctx.send(error)

	# Attempt to be a dad for those who are "back"
	@commands.Cog.listener()
	async def on_message(self, message):


		# If the bot is reading a message from a bot
		if message.author.bot: return

		# If the bot is reading it's own message
		if message.author == self.bot.user: return

		# Find everything including the "back ..."
		is_back = re.search(r"(^| )i('|a| a)?m ?(back [^\n]+|back$|back\s)", message.content)

		# Find everything afer the "i'm "
		# is_back = re.search(r"i('|a| a)?m (.*)", message.content, re.IGNORECASE)

		# Send message
		if is_back:
			await message.channel.send("Hi {} I'm Anna Li".format(is_back.group(3)))

		print(message.content)

		# Spooky
		if "spooky" in message.content.lower() or "spooked" in message.content.lower():
			await message.add_reaction('👻')
			await asyncio.sleep(2)
			await message.remove_reaction('👻', self.bot.user)


# Give the cog to the bot
def setup(bot):
	bot.add_cog(MiscCog(bot))