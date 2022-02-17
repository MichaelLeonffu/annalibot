# misc.py

# Just some random commands (loose ends)


# This is the discord
import discord
from discord.ext import commands
# Regex
import re
# AsyncIo
import asyncio
# random
import random
# datetime
import datetime


# Our simple cog
class MiscCog(commands.Cog, name="Misc"):
    """MiscCog"""

    # Allows us to have bot defined and passed in
    def __init__(self, bot):
        self.bot = bot

        # Placed here to run code only once
        # Generate the morse code pairs dot = . dash = -
        code = ".- -... -.-. -.. . ..-. --. .... .. .--- -.- .-.. -- \
        -. --- .--. --.- .-. ... - ..- ...- .-- -..- -.-- --.. \
        ----- .---- ..--- ...-- ....- ..... -.... --... ---.. ----. \
        --..-- ..--.. -.-.--"

        alphanum = "abcdefghijklmnopqrstuvwxyz0123456789,?!"

        # Pair the values
        pairs = [(c, alphanum[i]) for i, c in enumerate(code.split())] +\
          [(alphanum[i], c) for i, c in enumerate(code.split())]

        # Generate the dicts/LUT
        self.morse_lut = {pair[0]: pair[1] for pair in pairs}

        # Add spaces
        self.morse_lut.update({" ": "\\", "\\": " "})

    # @commands.command(
    #     name='math',
    #     aliases=['m'],
    #     brief='Does math',
    #     description='So Anna Li can do math, what can you do?',
    #     help='Anna Li can do your math! (Supported + - * /)',
    #     rest_is_raw=True)
    # async def _math(self, ctx, *args):

    #     # Remove all the space and join together
    #     args = ''.join(args)

    #     # Separating between numbers and operators
    #     acc = ""
    #     infix = []
    #     for arg in args:
    #         if arg.isnumeric():
    #             acc += arg
    #         else:
    #             infix.append(acc)
    #             infix.append(arg)
    #             acc = ""

    #     # This is likely given in infix notation
    #     operator_stack, operand_stack = [], []

    #     # Valid operators currently
    #     operators = "- + / * ( )".split(' ')

    #     # Precedence rules PEMDAS
    #     precedence_rules = {op: operators.index(op) for op in operators}

    #     # Algorithm
    #     for arg in infix:
    #         if arg in operators:			# Operator
    #             while precedence_rules[operator_stack[-1:]] >= arg:
    #                 top_op = operator_stack.pop()
    #                 op1, op2 = operand_stack.pop(), operand_stack.pop()
    #                 operand_stack.append(eval("op1 top_op op2"))

    #         else:							# Operand
    #             # If it is not a valid operand then stop
    #             if not arg.isnumeric():
    #                 return await ctx.send("Invalid operand: {}".format(arg))
    #             operand_stack.append(arg)

    #     await ctx.send(arg)


    @commands.command(
     name='mypic',
     # aliases=['mypic'],
     brief='Show this profile pic',
     description='You wana see yourself?',
     help='Lets get that for you')
    async def _mypic(self, ctx, size=1024):
        await ctx.send(ctx.author.avatar_url_as(size=size))

    @commands.command(
     name='all_emotes',
     aliases=['emotes'],
     brief='Get all emotes on this server',
     description='You cant do this yourself can you...',
     help='Lets get that for you')
    async def _all_emotes(self, ctx):

        # Get guild
        emotes =  ["<:1:{}>".format(emoji.id) for emoji in ctx.guild.emojis if not emoji.animated]
        emotes += ["<a:1:{}>".format(emoji.id) for emoji in ctx.guild.emojis if emoji.animated]

        # Group up until limit is reached; max char limit - offset
        # LIMIT = 2000 - 30
        # messages = []
        # message = ''
        # for emote in emotes:
        #     if len(message) > LIMIT:
        #         messages.append(message)
        #         message = ''
        #     message += emote
        # messages.append(message)

        # Group by 25 emotes at a time
        messages = []
        message = ''
        for i, emote in enumerate(emotes):

            message += emote
            message += "\n\n" if ((i+1) % 9 == 0) else "     "

            if (i+1) % 27 == 0:
                messages.append(message)
                message = ''

        messages.append(message)

        # Send it
        for message in messages:
            await ctx.send(message)

    @commands.command(
     name='yourpic',
     # aliases=['yourpic'],
     brief='Show your profile pic',
     description='You wana see someone else?',
     help='Lets get that for you')
    async def _yourpic(self, ctx, mention, size=1024):
        await ctx.send((await commands.MemberConverter().convert(ctx, mention)).avatar_url_as(size=size))

    # @commands.command(
    #  name='nanitime',
    #  aliases=['nt'],
    #  brief='Shows what time it is in a time zone',
    #  description='Only supports Korea and California',
    #  help='I used datetime just for you!')
    # async def _nanitime(self, ctx, tz=""):
    #     import datetime
    #     import pytz

    #     input_tz = str(tz).lower()

    #     record = {
    #      "california": "America/Los_Angeles",
    #      "korea": "Asia/Seoul"
    #     }

    #     # 🌅🌄🌃🌌🌆🏙🎇🎆🇰🇷🇺🇸

    #     # One record only
    #     if input_tz in record:
    #         tz_datetime = datetime.datetime.now(pytz.timezone(record[input_tz]))
    #         return await ctx.send("{}: {}".format(input_tz.upper(), tz_datetime.strftime("%Y-%m-%d %H:%M:%S")))

    #     # All records
    #     for input_tz in record:
    #         tz_datetime = datetime.datetime.now(pytz.timezone(record[input_tz]))
    #         await ctx.send("{}: {}".format(input_tz.upper(), tz_datetime.strftime("%Y-%m-%d %H:%M:%S")))

    #     # await ctx.send("invalid choice, try: `nt california` or `nt korea`")

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

    @commands.command(
     name='say',
     aliases=['tell'],
     brief='Anna Li says something',
     description='Anna Li can say something for you if you are shy',
     help='Do not use profanity!')
    async def _say(self, ctx, *, phrase):
        await ctx.message.delete()
        await ctx.send(phrase)

    @commands.command(
     name='morse_code',
     aliases=['morse'],
     brief='Anna Li translates to/from morse code',
     description='This way you can beep boop',
     help='Hopefully it is not a long message')
    async def _morse_code(self, ctx, *, phrase):

        # For all the letters
        phrase = phrase.lower()
        space = " "

        # Check if it is all morse coded (".- \")
        if len(set(phrase) - {'.', ' ', '\\', '-'}) == 0:
            # Split makes it work by multi characters vs single ones
            phrase = phrase.split()
            space = ""

        morse = ""

        # Convert to mose code
        for char in phrase:
            if char in self.morse_lut:
                morse += self.morse_lut[char] + space
            else:
                morse += char

        await ctx.send("`{}`".format(morse))

    @_mypic.error
    @_all_emotes.error
    @_yourpic.error
    @_add.error
    @_mul.error
    @_div.error
    @_say.error
    @_morse_code.error
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

        # Spooky
        if "spooky" in message.content.lower() or "spooked" in message.content.lower():
            await message.add_reaction('👻')
            await asyncio.sleep(1)
            await message.remove_reaction('👻', self.bot.user)

        # Detect if message is morse (only applies to messages with length > 3)
        if len(message.content) > 5 and len(set(message.content) - {'.', ' ', '\\', '-'}) == 0:
            await self._morse_code(message.channel, phrase=message.content)


# Give the cog to the bot
def setup(bot):
    bot.add_cog(MiscCog(bot))
