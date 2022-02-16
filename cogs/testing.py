# testing.py

# Experimental code


# Config
import config.config as config
# This is the discord
import discord
from discord.ext import commands
# Context
import contextvars as ctxvar


# Our test cog
class TestCog(commands.Cog, name="testing"):
    """TestCog"""

    # Allows us to have bot defined and passed in
    def __init__(self, bot):
        self.bot = bot

        # Config
        self.CONFIG_var = ctxvar.ContextVar('CONFIG')
        self.CONFIG_var.set(config)



    @commands.command()
    async def test(self, ctx, *args, hidden=True):
        await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))

    # If someone @annalibot then tell them the help prompt
    @commands.Cog.listener()
    async def on_message(self, message):

        # If the bot is reading it's own message
        if message.author == self.bot.user:
            return


        # import pprint
        # pprint.pprint(message.content)

        # If it only mentions 1 person and that person is the bot
        # (redundancy but also checking if that message is only @ the bot)
        # if len(message.mentions) == 1 and self.bot.user.id == message.mentions[0].id:
        if message.content == ("<@!%s>" % self.bot.user.id):
            await message.channel.send("Wah? use %help")

    # Print out a cached message
    @commands.command(
     name='repeat',
     aliases=['peat'],
     brief='Repeats a message to consol',
     description='Helps testing and debugging',
     help='repeat [message_id]',
     usage='lol what')
    async def _repeat(self, ctx, message_id):

        await ctx.message.reply('Hello!', mention_author=True)


        # Find the message
        message = await commands.MessageConverter().convert(ctx, message_id)

        print("refernce of", message.reference)

        await ctx.send("✅ Message found!")

        print("\n\nmessage", message)

        if len(message.embeds) < 1:
            return await ctx.send("⚠️ No embed")

        print("\n\nembed", message.embeds[0].to_dict())

        print("\n\nreacts", message.reactions)

    @commands.command(
     name='embed',
     aliases=['em'],
     brief='Embed testing',
     description='Attempt to make things look pretty',
     help='And colorful',
     usage='%mul(int a, int b)')
    async def _embed(self, ctx):
        embed = discord.Embed(
         title='Title',
         description='description',
         url='https://cdn.discordapp.com/attachments/618692088137252864/739352223619743882/bbffbb.png',
         colour=discord.Colour.red()
        )

        embed.set_image(url='https://cdn.discordapp.com/attachments/618692088137252864/739351037781213204/ffbbff.png')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/618692088137252864/739352396144312360/bbbbff.png')
        embed.set_footer(text='footer')

        embed.set_author(name='Author')
        embed.set_author(name='Author')
        embed.add_field(
         name='field name',
         value='value',
         inline=False
        )
        embed.add_field(
         name='field name2',
         value='value2 inline',
         inline=True
        )
        # await ctx.send()
        await ctx.send(embed=embed)


    @commands.command(
     name='file',
     aliases=['f'],
     brief='File testing',
     description='Uploading a file (so that I can use the url later)',
     help='Teehee',
     usage='%file')
    async def _file(self, ctx):

        return await ctx.send("BROKEN; image no longer exists in path.")
        file = discord.File("images/meowpudding.jpg", filename="meowpudding.jpg", spoiler=False)

        # If the USER_ID in the config is 0 (default) then send
        # the file to the user who sent the message
        user_id = self.CONFIG_var.get().USER_ID
        if user_id == 0:
            user_id = ctx.message.author.id

        # message = await ctx.channel.send("file: " + str(file), file=file)

        # Begin loophole
        # Find our user (not possible to send message to self, so sending it to defined user)

        return await ctx.send("BROKEN; 1.50 requires INTENTS")

        user = self.bot.get_user(user_id)
        # Create dm if there isn't one
        if user.dm_channel == None:
            await user.create_dm()
        # Send a message to this user (ourself)
        message = await user.dm_channel.send("file: " + str(file), file=file)


        embed = discord.Embed(
         title='Meow',
         description='And spagethit',
         # url='show a url in the embed',
         colour=discord.Colour.red()
        )

        embed.set_image(url=message.attachments[0].url)
        embed.set_footer(text='(meow)')
        embed.add_field(
         name='field name',
         value='value',
         inline=False
        )
        await ctx.send(embed=embed)


    # Attempting to use othe people emotes
    @commands.command(
     name='emote',
     aliases=['emo'],
     brief='Emote testing',
     description='Using custom emotes',
     help=':)',
     usage='%emote')
    async def _emote(self, ctx):

        emojis = self.CONFIG_var.get().EMOJI

        await ctx.send(" ".join([emo for emo in emojis]))


    # @bot.command(name='eval')
    # @commands.is_owner()
    # async def _eval(ctx, *, code):
    # 	"""A bad example of an eval command"""
    # 	await ctx.send(eval(code))


    @commands.command()
    async def pages(self, ctx):
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



# Give the cog to the bot
def setup(bot):
    bot.add_cog(TestCog(bot))
