# cat.py

# cat features


# Config
import config.config as config
# This is the discord
import discord
from discord.ext import commands
# Time
import time
import datetime
# mongodb
import pymongo
# AsyncIo
import asyncio
# random
import random


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

# Our cat cog
class CatCog(commands.Cog, name="Cat"):
    """CatCog"""

    # Allows us to have bot defined and passed in
    def __init__(self, bot):
        self.bot = bot

        # Connect the mongodb client
        self.client = pymongo.MongoClient(config.DB_URI)
        self.db = self.client.cat



    async def fetch_user(self, user, ctx):


        # Fetch the user data from the db
        user_data = self.db.catList.find_one({
            '_id': {
                'user': user.id,
                'guild': ctx.message.channel.guild.id
            },
        })

        # End
        if user_data != None:
            return user_data

        # Some fancy messages
        message = await ctx.send("No data found for you!")
        await asyncio.sleep(1)
        await message.edit(content="Initializing suprise...")

        # If user is not found then inialize it:
        init_data_doc = {
            '_id': {
                'user': user.id,
                'guild': ctx.message.channel.guild.id
            },
            'cats':[],
            'listName': '',
            'nyaPoints': 500,
            'dailyNya': datetime.datetime(1, 1, 1, 0, 0)
        }

        # Attempt to add this user to the database
        insert_result = self.db.catList.insert_one(init_data_doc)

        # Some fancy messages
        await asyncio.sleep(1)
        await message.edit(content="Welcome to cat cafe!!")
        await asyncio.sleep(1)
        await message.delete(delay=1)

        # Fetch the user data from the db
        user_data = self.db.catList.find_one({
            '_id': insert_result.inserted_id
        })

        return user_data


    async def fetch_guild(self, ctx):


        # Fetch the guild data from the db
        guild_data = self.db.catfig.find_one({
            '_id': ctx.message.channel.guild.id
        })

        # End
        if guild_data != None:
            return guild_data

        # Some fancy messages
        message = await ctx.send("No guild data found!")
        await asyncio.sleep(1)
        await message.edit(content="Initializing data for this guild...")

        # If guild is not found then inialize it:
        init_data_doc = {
            '_id': ctx.message.channel.guild.id,
            'catTypes': [],
            'dailyNyaRate': 50,
            'catAdpotCost': 500
        }

        # Attempt to add this user to the database
        insert_result = self.db.catfig.insert_one(init_data_doc)

        # Some fancy messages
        await asyncio.sleep(1)
        await message.edit(content="Welcome to cat cafe!!")
        await asyncio.sleep(1)
        await message.delete(delay=1)

        # Fetch the guild data from the db
        guild_data = self.db.catfig.find_one({
            '_id': insert_result.inserted_id
        })

        return guild_data


    @commands.command(
        name='catlist',
        aliases=['clist', 'catl', 'cl'],
        brief='Lists your cats',
        description='Shows you all your cats!',
        help='Nyas!',
        usage='(Optional) user')
    async def _catlist(self, ctx, *mention):


        time_start = time.time()

        # Remove spaces
        mention = ' '.join(mention)

        user = ctx.message.author
        if len(mention) > 0:
            user = await commands.MemberConverter().convert(ctx, mention)

        # Get user data
        user_data = await self.fetch_user(user, ctx)

        # Make the embed
        embed = discord.Embed(
            colour=discord.Colour.orange()
        )

        # Set user image
        embed.set_thumbnail(url=user.avatar_url_as(size=1024))

        # Cat list name
        list_name = user_data['listName']
        if len(list_name) < 1:
            list_name = "Cat List"
        embed.set_author(name="{}'s {}".format(user.name, list_name))

        result = self.db.catList.aggregate([
            {
                '$match': {
                    '_id': {
                        'user': user.id,
                        'guild': ctx.message.channel.guild.id
                    }
                }
            }, {
                '$unwind': {
                    'path': '$cats',
                    'includeArrayIndex': 'order'
                }
            }, {
                '$lookup': {
                    'from': 'cats',
                    'localField': 'cats',
                    'foreignField': '_id',
                    'as': 'cat'
                }
            }, {
                '$group': {
                    '_id': {
                        'user': '$_id.user',
                        'guild': '$_id.guild',
                        'nyaPoints': '$nyaPoints',
                        'listName': '$listName'
                    }, 
                    'cats': {'$push': { '$arrayElemAt': ['$cat', 0]}}
                }
            }
        ])

        result = list(result)[0]

        # # For each cat
        # for cat in result['cats']:

        # 	# Unpack the values
        # 	cat_type = cat['catType']

        # 	# Print their rolls and claims
        # 	embed.add_field(
        # 		name= cat_type,
        # 		value="old",
        # 		inline=False
        # 	)

        catsTypes = "\n".join([cat['catType'] for cat in result['cats']])
        embed.add_field(
            name="Cat List",
            value="\n\n" + catsTypes,
            inline=False
        )

        # Report the time it took to compute this
        time_end = time.time()
        compute_time = "Time: " + str(round(time_end - time_start, 2)) + "s"
        embed.set_footer(text=compute_time)

        # Send the embed stats
        await ctx.send(embed=embed)


    @commands.command(
        name='dailynya',
        aliases=['daily'],
        brief='Daily Nya',
        description='Get your Daily Nya every 12 hours',
        help='Nyas attract cats!',
        usage='(Optional) user')
    async def _dailynya(self, ctx):


        time_start = time.time()
        user = ctx.message.author

        # Get user data
        user_data = await self.fetch_user(user, ctx)

        # Take time
        today = datetime.datetime.utcnow()
        # Remove the seconds and micoseconds
        today = today.replace(second=0, microsecond=0)
        cool_down = datetime.timedelta(days=0, hours=12)
        available = user_data['dailyNya'] + cool_down

        # print("SIOMETHIGN" + str(available))

        # available = utc_to_local(available)

        # Check if user cant dailyNya
        if available > today:
            time_left = available - today
            return await ctx.send("Next \%dailynya reset in {}h {} min.".format(time_left.days * 24 + time_left.seconds//3600, (time_left.seconds%3600)//60))

        # Get guild data
        guild_data = await self.fetch_guild(ctx)

        # Generate a random amount of nyaPoints basied on the guild catfig
        base_rate = guild_data['dailyNyaRate']

        # Randomize
        tier_random = random.randint(1, 10000)

        # Where tier 4 is highest and 0 is lowest
        tier = (tier_random <= 1*base_rate) + (tier_random <= 3*base_rate) + (tier_random <= 7*base_rate) + (tier_random <= 15*base_rate)
        
        random_nya_points = (tier*tier+1)*500 + random.randint(-100, 100)

        # Query data (Makes it more atomic)
        query = {
            '_id': user_data['_id'],
            'dailyNya': user_data['dailyNya']
        }

        # Give user their nyaPoints and react to the message; also reset their timmer
        update = {
            "$inc": { 'nyaPoints': random_nya_points},
            "$set": { 'dailyNya': today}
            # "$currentDate": { 'dailyNya': 'timestamp'}
        }

        # Update the data
        result = self.db.catList.update_one(query, update)

        # # Report the time it took to compute this
        # time_end = time.time()
        # compute_time = "Time: " + str(round(time_end - time_start, 2)) + "s"

        # # Some fancy messages
        # message = await ctx.send(compute_time)
        # await asyncio.sleep(1)
        # await message.delete(delay=1)

        # Error checking
        if result.modified_count > 1:
            return await ctx.send("TELL A MOD, THIS IS AN ERROR!!!!!! [AdoptCat, Result.modified_count]")

        if result.modified_count != 1:
            return await ctx.send("Are you trying to break the system?")

        expressions = ['', "XD Pog!!", "Wow!!", "Omg that's so cool", "WOAHHHHHH WOWOWOWOOWOWW"]

        # Notify user
        await ctx.message.add_reaction('🎊')
        await ctx.send("{} +**{}**:nyaPoints:added to your nyallet! (**{}** total)".format(expressions[tier], random_nya_points, random_nya_points + user_data['nyaPoints']))


    # @_dailynya.error
    # async def _dailynya_error(self, ctx, error):
    # 	if isinstance(error, commands.BadArgument):
    # 		await ctx.send(error)
    # 	else:
    # 		print(error)

    @commands.command(
        name='adpotcat',
        aliases=['ac'],
        brief='Adpots a cat',
        description='Costs x nyaPoints',
        help='Adpot a cat today!')
    async def _adpotcat(self, ctx):


        time_start = time.time()
        user = ctx.message.author

        # ISSUE with atomic (reading the cost of cat roll and the getting user amount!)

        # Get user data
        user_data = await self.fetch_user(user, ctx)

        # Get guild data
        guild_data = await self.fetch_guild(ctx)


        # Check if this user cannot afford the cat;
        if user_data['nyaPoints'] < guild_data['catAdpotCost']:
            return await ctx.send("You need an additional {} :nyaPoints:".format(guild_data['catAdpotCost'] - user_data['nyaPoints']))

        # Should try to aggregate data from guild and default
        # If it fails then we know to initalize this guild
        # More maybe initalizing a guild should be when the bot joins the server...

        # Get default guild data I should optimize this out?
        default_guild_data = self.db.catfig.find_one({'_id': 0})


        # For now I'll just combine the data together into a single array
        cat_types = default_guild_data['catTypes'] + guild_data['catTypes']

        # Draw a random cat type (this is random for now but will be less random later)
        cat_type = cat_types[random.randrange(0, len(cat_types))]
        # cat_type_choices = [cat_types[random.randrange(0, len(cat_types))], cat_types[random.randrange(0, len(cat_types))], cat_types[random.randrange(0, len(cat_types))]]

        # # Generate the message gatcha choices
        # message = await ctx.send("3 cats appeared!! Choose: **{}** cat, **{}** cat, and **{}** cat!".format(cat_type_choices[0], cat_type_choices[1], cat_type_choices[2]))
        # await message.add_reaction('1️⃣')
        # await message.add_reaction('2️⃣')
        # await message.add_reaction('3️⃣')

        # return

        # Generate the random cat
        random_cat = {
            # '_id': unique,
            'catType': cat_type,
            'guild': ctx.message.channel.guild.id,
            'history': [
                {
                    'owner': ctx.message.author.id,
                    'obtained': 'rolled',
                    'datetime': datetime.datetime.utcnow().replace(microsecond=0),
                    'guild': ctx.message.channel.guild.id,
                    'channel': ctx.message.channel.id
                }
            ],
            'nickname': ''
        }

        result = self.db.cats.insert_one(random_cat)

        # Query data (Makes it more atomic)
        query = {
            '_id': user_data['_id'],
            'nyaPoints': user_data['nyaPoints']
        }

        # Deduct nyaPoints, add cat
        update = {
            "$inc": { 'nyaPoints': -guild_data['catAdpotCost']},
            "$push": { 'cats': result.inserted_id}
        }

        # Update the data
        result = self.db.catList.update_one(query, update)

        # Error checking
        if result.modified_count > 1:
            return await ctx.send("TELL A MOD, THIS IS AN ERROR!!!!!! [AdoptCat, Result.modified_count]")

        if result.modified_count != 1:
            return await ctx.send("Are you trying to break the system?")

        # Notify user
        await ctx.message.add_reaction('🎊')
        await ctx.send("Congratulations you've adpoted your first **{}** cat!".format(random_cat['catType']))


# Give the cog to the bot
def setup(bot):
    bot.add_cog(CatCog(bot))