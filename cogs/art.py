# art.py

# art gallery

# Schema located at /docs/schema/art.json

# Config
import numbers
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
from bson.objectid import ObjectId
# pprint
import pprint
# io
import io
# aiohttp
import aiohttp


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

# Our art cog
class ArtCog(commands.Cog, name="Art"):
    """ArtCog"""

    # Allows us to have bot defined and passed in
    def __init__(self, bot):
        self.bot = bot

        # Connect the mongodb client
        self.client = pymongo.MongoClient(config.DB_URI)
        self.db = self.client.art
        self.collection = self.db.art

    async def art_upload_routine(self, ctx, 
        guild_id: int = None,
        channel_id: int = None,
        message_id: int = None,
        url: str = None,
        owner: int = None,
        uploader: int = None,
        datetime_created = None,
        tags: list[str] = [],
        series: str = "",
        title: str = "",
        caption: str = ""
    ):
        """
        Uploading art protocol; other functions should call this generic function one
        Validation is done here

        Parameters:
            required: guild_id, channel_id, message_id, url, owner, uploader
            everything else is optional, default: bin, null, null, null
        """

        # Should do some validation here and throw error if mistakes
        # Check required fields
        if not (guild_id and channel_id and message_id and url and owner and uploader):
            raise Exception("Required fields not provided")

        # Check url

        # If tags is too long or empty then it's wrong
        if len(tags) > 32:
            return await ctx.send("⚠️ Must be less than 32 tags, given: " + len(tags))

        for tag in tags:
            if len(tag) == 0 or len(tag) > 32:
                return await ctx.send("⚠️ Tags length must be between 1 and 32 characters, but given: " + len(tag) + " for tag " + tag[:40])

        # Convert tags to lowercase
        tags = [tag.lower() for tag in tags]

        # Check tag type; only alphanumeric and underscore
        for tag in tags:
            if not re.match(r"^[a-z0-9_]+$", tag):
                return await ctx.send("⚠️ Tags must be alphanumeric and underscore only, but given: " + tag)

        # Upload document, Prepare doc
        doc = {
            '_id': {
                'guild': guild_id,
                'channel': channel_id,
                'message': message_id,
            },
            'url':          url,
            'owner': 		owner,
            'uploader': 	uploader,
            'tags': 		tags,
            'datetime_created':			datetime_created if datetime_created else datetime.datetime.utcnow(),
            'datetime_uploaded':		datetime.datetime.utcnow(),
            'series': 	    series,
            'title': 	    title,
            'caption': 	    caption
        }

        # Upload data to server
        res = self.collection.insert_one(doc)

        return res

    # TODO make upsert/update protocol should be able to use similar logic from upload routine.

    # Commands to interface feature

    def parse_tags(mess: str):
        """
        Parses and returns parsed and the mess after removing what was parsed or default if no parse found
        """
        tags = ["bin"] # Optional: Look for the first "#something" pattern

        pattern = re.compile(r"#\w+")
        tags = re.findall(pattern, mess)
        mess = re.sub(pattern, '', mess)

        # If there are no tags then use the first uppercase word as the title
        if len(tags) < 1:
            pattern = re.compile(r"[A-Z]\w*")
            res = re.search(pattern, mess)
            if res:
                tags = [res.group()]
                mess = re.sub(pattern, '', mess, count=1)

        # If there are no tags then use the default tag
        if len(tags) < 1:
            tags = []
        else: # Remove '#' from tags
            tags = [tag[1:] for tag in tags]

        return tags, mess

    def parse_series(mess: str):
        """
        Parses and returns parsed and the mess after removing what was parsed or default if no parse found
        """
        series = "null" # Optional: Look for something that has a number and no hashtag either "123" or "abc123" or "123abc"

        pattern = re.compile(r"\w*\d+\w*")
        res = re.search(pattern, mess)
        if res:
            series = res.group()
        mess = re.sub(pattern, '', mess, count=1)

        return series, mess

    def parse_title(mess: str):
        """
        Parses and returns parsed and the mess after removing what was parsed or default if no parse found
        """
        title = "null" # Optional: The longest series of words which have capital letters on the same line

        pattern = re.compile(r"(([A-Z]\w*[^\S\r\n]*)+)")
        titles = [match_pair[0] for match_pair in re.findall(pattern, mess)]
        # Get max length title
        if len(titles) > 0:
            title = max(titles, key=len)
            mess = re.sub(title, '', mess)
            title = title.strip()

        return title, mess

    def parse_caption(mess: str):
        """
        Parses and returns parsed and the mess after removing what was parsed or default if no parse found
        """
        caption = "" # Optional: any section of words that isn't contained above

        caption = mess.strip()

        return caption, ""

    def parse_art_message(message_content: str):
        """
        Parses the message and returns a dictionary of the data

        tags = ["bin"] # Optional: Look for the first "#something" pattern
        series = "null" # Optional: Look for something that has a number and no hashtag either "123" or "abc123" or "123abc"
        title = "null" # Optional: series of words which have capital letters
        caption = "null" # Optional: any section of words that isn't contained above

        Example mesage
        Goth E-Girl #terrinktober22 Day: 1 Featuring something sick
        Should parse as: '#terrinktober22' '1' 'Goth E-Girl' 'Featuring something sick' | 'Day:'
        """

        # Parse message content

        # Find and remove all tags
        tags, message_content = ArtCog.parse_tags(message_content)

        # Find and remove series
        series, message_content = ArtCog.parse_series(message_content)

        # Find and remove title
        title, message_content = ArtCog.parse_title(message_content)

        # The remainder is the caption
        caption, message_content = ArtCog.parse_caption(message_content)

        # TODO: fix the issues where there are double spaces etc.

        return tags, series, title, caption

    async def art_fetch_display(self, guild, channel, message):
        """
        Used after finding an id of an artwork that has been uploaded
        
        Fetched the art and displays in a embed style message with all data shown
        """

        id = {
            'guild': guild,
            'channel': channel,
            'message': message,
        }

        # Fetch the art
        res = self.collection.find_one({'_id': id})

        if not res:
            raise Exception("No art found with id: " + str(id))

        embed = discord.Embed(
         title="{}: {}".format(res['title'], res['series']),
         description=res['caption'],
         url=res['url'],
         colour=discord.Colour.random()
        )

        embed.set_image(url=res['url'])
        # embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/618692088137252864/739352396144312360/bbbbff.png')
        embed.set_footer(text='#'+", #".join(res['tags']))

        user = await self.bot.fetch_user(res['owner'])
        embed.set_author(name=user.name)

        return embed

    @commands.command(
        name='art_reply_upload',
        aliases=['aru'],
        brief='Upload your art using a reply!',
        description='Then we can see all the art together',
        help='Reply to a message that has art and use "annali aru", "aru q" for quiet, and d for delete')
    async def _art_reply_upload(self, ctx, opts: str = ""):

        # Should have a reply
        if ctx.message.reference is None:
            return await ctx.send("⚠️ No reply found!")

        # Convert mess_id to message
        message = await commands.MessageConverter().convert(ctx, str(ctx.message.reference.message_id))

        # Read in the file attachment
        if len(message.attachments) < 1:
            raise ValueError("Wrong number of files: " + str(len(message.attachments)) + " < 1")

        # Get information from parsing message content
        message_content = message.content

        tags, series, title, caption = ArtCog.parse_art_message(message_content)

        # TODO: Give users the option to update what was uploaded. If certain fields were not found
        # TODO: Show uploaded art in an embed with the option to delete the embed later.

        # Upload document
        res = await self.art_upload_routine(
            ctx = ctx,
            guild_id = message.guild.id if message.guild else None,
            channel_id = message.channel.id,
            message_id = message.id,
            url = message.attachments[0].url,
            owner = message.author.id,
            uploader = ctx.message.author.id,
            datetime_created = message.created_at,
            tags = tags,
            series = series,
            title = title,
            caption = caption
        )

        # Delete original message
        if 'd' in opts:
            await ctx.message.delete()

        # Failed upload
        if not res.acknowledged:
            return await ctx.send("⚠️ Art upload failed")

        # Show uploaded data
        if res and 'q' not in opts:
            await ctx.send("✅ Art uploaded successfully")
            try:
                embed = await self.art_fetch_display(**res.inserted_id)
            except Exception as err:
                return await ctx.send("⚠️ " + str(err))

            # await ctx.send()
            return await ctx.send(embed=embed)


    @commands.command(
        name='art_upload',
        aliases=['au'],
        brief='Upload your art!',
        description='Then we can see all the art together',
        help='Provide the message id, you cannot delete the message otherwise the art will be lost')
    async def _art_upload(self, ctx, *messages_id):

        # deprecated for now.
        return await ctx.send("⚠️ This command is deprecated for now")

        tags = "bin"

        # If tags is too long or empty then it's wrong
        if len(tags) == 0 or len(tags) > 16:
            return await ctx.send("⚠️ tags length is bad size: 1-16 inclusive, but given: ", len(tags))

        async def convert_to_message(mess_id):
            # Convert mess_id to message
            mes = await commands.MessageConverter().convert(ctx, mess_id)

            # Read in the file attachment
            if len(mes.attachments) < 1:
                raise ValueError("Wrong number of files: " + str(len(ctx.message.attachments)) + " < 1")

            return mes

        messages = [await convert_to_message(mes) for mes in messages_id]

        # Find the attachment
        # attachments = [attachment.url for attachment in mes.attachments for mes in messages]

        # docs 
        docs = []
        for message in messages:
            for attachment in message.attachments:
                # Prepare doc
                docs.append({
                    'owner': 		message.author.id,
                    'url': 			attachment.url,
                    'bin': 			tags,
                    'datetime':		message.created_at
                })

        # Upload data to server
        self.collection.insert_many(docs)
        # await ctx.send(" ".join(attachments))
        # await ctx.send(docs)

        # Check upload result
        await ctx.send("✅ {} Art(s) uploaded!!!".format(len(docs)))

    @commands.command(
        name='art_view',
        aliases=['av'],
        brief='View your art!',
        description='Then we can see all the art together',
        help='Provide the author')
    async def _art_view(self, ctx, owner=None, tags="bin", limit=100):

        # Get most recent art from user
        res = list(self.collection.find({'owner': ctx.author.id}).sort('datetime_created', -1).limit(1))

        if len(res) < 1:
            return await ctx.send("⚠️ No art found for you; Upload art using 'annali art_reply_upload'")

        # Demo only
        await ctx.send("⚠️ Incomplete command; shows most recent uploaded art")

        try:
            embed = await self.art_fetch_display(**res[0]['_id'])
        except Exception as err:
            return await ctx.send("⚠️ " + str(err))

        # await ctx.send()
        return await ctx.send(embed=embed)

        # Deprecated for now
        return await ctx.send("⚠️ This command is deprecated for now")

        tags = "bin"

        # If tags is too long or empty then it's wrong
        if len(tags) == 0 or len(tags) > 16:
            return await ctx.send("⚠️ tags length is bad size: 1-16 inclusive, but given: ", len(tags))

        # If no argument is given for the author then fill in as the calling user
        if author_id == None:
            user = ctx.message.author
        else:
            user = await commands.UserConverter().convert(ctx, author_id)

        # Search the database for this author
        return await ctx.send("Not ready yet; will send you the link to the art gallery")

    @commands.command(
        name='art_edit',
        aliases=['ae'],
        brief='Edit your art!',
        description='Update fields of the art, you can reply to a message which contains the art to edit it',
        help='Update the fields of the art')
    async def _art_edit(self, ctx,
        # Use this to search for the art
        guild_id: int = None,
        channel_id: int = None,
        message_id: int = None,
        # url: str = None, Cannot be changed
        # owner: int = None, Cannot be changed for now
        # uploader: int = None, Cannot be changed for now
        # datetime_created = None, Cannot be changed for now
    ):
        """
            Allow users to update the art metadata
                tags: list[str] = [],
                series: str = "",
                title: str = "",
                caption: str = ""

            Each section will be broken into a line each starting with:
                command and _id, title, series, tags, caption

            This is interesting because cannot leave it empty since discord
            will remove the white space; therefore if the message ends with a
            ... then it would be considered empty eg:
            &ae 1234567890 1234567890 1234567890
            ...

        """

        # Check for id arguments
        if not(guild_id and channel_id and message_id):
            return await ctx.send("⚠️ Missing _id arguments")

        query = {
            '_id': {
                'guild': guild_id,
                'channel': channel_id,
                'message': message_id,
            }
        }

        # Find and the document (not atomic)
        res = self.collection.find_one(query)

        # If no document is found then return
        if res == None:
            return await ctx.send("⚠️ No art found")

        # Check if this user is either the uploader or the owner
        if ctx.message.author.id not in [res['uploader'], res['owner']]:
            return await ctx.send("⚠️ You are not the owner or uploader of this art")

        # Check for metadata arguments
        if ctx.message.content.count('\n') < 1:
            return await ctx.send("⚠️ Missing metadata arguments, if empty then use ...")

        # Parse the metadata arguments
        metadata = ctx.message.content.split('\n')

        tags = series = title = caption = None

        if len(metadata) > 1:
            if metadata[1] == "...":
                tags = []
            else:
                tags, mess = ArtCog.parse_tags(metadata[1])

        if len(metadata) > 2:
            if metadata[2] == "...":
                series = ""
            else:
                series = metadata[2].split()[0][:32] # Only take the first word

        if len(metadata) > 3:
            if metadata[3] == "...":
                title = ""
            else:
                title = metadata[3][:64]

        if len(metadata) > 4:
            if metadata[4] == "...":
                caption = ""
            else:
                caption = "\n".join(metadata[4:])[:1024]


        # Update the document
        # Find and update the document
        res = self.collection.update_one(
            query,
            {
                '$set': {
                    'tags': tags,
                    'series': series,
                    'title': title,
                    'caption': caption,
                }
            }
        )

        # Think about showing the art after editing
        return await ctx.send("✅ Art updated")

    @_art_reply_upload.error
    @_art_upload.error
    @_art_view.error
    async def _any_error(self, ctx, error):
        await ctx.send('⚠️' + str(error))
        # if isinstance(error, commands.BadArgument):
        # 	await ctx.send(error)
        # else:
        # 	print(error)

# Give the cog to the bot
def setup(bot):
    bot.add_cog(ArtCog(bot))
