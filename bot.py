import os
import discord
import asyncpraw
import asyncprawcore
from cs50 import SQL
from dotenv import load_dotenv
from discord.ext import commands, tasks
from pretty_help import DefaultMenu, PrettyHelp

# Initialisation
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ID = os.getenv('CLIENT_ID')
SECRET = os.getenv('CLIENT_SECRET')
AGENT = os.getenv('USER_AGENT')

reddit = asyncpraw.Reddit(
    client_id=ID,
    client_secret=SECRET,
    user_agent=AGENT
)

# Defines a limit to the number of posts that can be requested in one go.
POST_LIMIT = 20

db = SQL("sqlite:///subinfo.db")

# Change prefix to whatever you want.
bot = commands.Bot(command_prefix='.', help_command=PrettyHelp(
    navigation=DefaultMenu(), color=discord.Colour.blurple(), index_title="Commands"))

"""Discord Reddit Integrator Bot"""

# Startup events.


@bot.event
async def on_ready():
    # Waiting until the bot is ready
    await bot.wait_until_ready()
    # Starting the loop
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='the eternal buzz of these random yellow carpeted rooms'))
    random_post.start()

# Sends messages for linked subreddits.


@tasks.loop(minutes=30)
async def random_post():
    sub_list = db.execute("SELECT * FROM interval_list")
    if sub_list:
        for sub in sub_list:
            subreddit = await reddit.subreddit(sub["sub"], fetch=True)
            num = sub["num"]

            async for submission in subreddit.random_rising():
                url = submission.url
                embed = discord.Embed(title=submission.title, url=url, value=submission.selftext)
                embed.set_image(url=url)
                channel = bot.get_channel(sub["channel_id"])
                await channel.send(embed=embed)
                num -= 1
                if not num:
                    break

# Handles subreddit searching.


class Reddit_Srch(commands.Cog, name='Reddit Submission Searching'):
    """srch, srchflr, r"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="srch", help="Searches for subreddit.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def isearch(self, ctx, sub, post_limit: int, post_sort):
        subreddit = await sub_check(sub)
        if not subreddit:
            await ctx.send("Subreddit does not exist.")
            return

        if post_limit > POST_LIMIT:
            post_limit = POST_LIMIT

        async for submission in getattr(subreddit, post_sort)(limit=None):
            if submission.stickied:
                continue

            url = submission.url
            embed = discord.Embed(title=submission.title, url=url, value=submission.selftext)
            embed.set_image(url=url)
            await ctx.send(embed=embed)

            post_limit -= 1
            if not post_limit:
                break
    
    # Different variant to accomodate flair searching.

    @commands.command(name="srchflr", help="Searches for submissions from subreddit, filtering by flair.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def isearchfilt(self, ctx, sub, post_limit: int, post_sort, flair):
        subreddit = await sub_check(sub)
        if not subreddit:
            await ctx.send("Subreddit does not exist.")
            return

        if post_limit > POST_LIMIT:
            post_limit = POST_LIMIT

        async for submission in getattr(subreddit, post_sort)(limit=None):
            if submission.stickied:
                continue

            if flair in submission.link_flair_text:
                url = submission.url
                embed = discord.Embed(title=submission.title, url=url, value=submission.selftext)
                embed.set_image(url=url)
                await ctx.send(embed=embed)

                post_limit -= 1
                if not post_limit:
                    break
            else:
                continue
        
        # decided not to make a flaired version of this, because it should be truly random.
        # i'm not lazy i don't know what you're talking about.
        
    @commands.command(name="r", help="Gets you a number of random posts.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def rand(self, ctx, sub, post_limit: int):
        subreddit = await sub_check(sub)
        if not subreddit:
            await ctx.send("Subreddit does not exist.")
            return

        if post_limit > POST_LIMIT:
            post_limit = POST_LIMIT

        while post_limit:
            submission = await subreddit.random()
            url = submission.url
            embed = discord.Embed(title=submission.title, url=url, value=submission.selftext)
            embed.set_image(url=url)
            await ctx.send(embed=embed)
            post_limit -= 1
        
    @commands.command(name="trending", help="Gets the top, trending posts from Reddit.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def trend(self, ctx, post_limit : int):
        if post_limit > POST_LIMIT:
            post_limit = POST_LIMIT
        subreddit = await reddit.subreddit("all")
        async for submission in subreddit.hot(limit=POST_LIMIT):
            url = submission.url
            embed = discord.Embed(title=submission.title, url=url, value=submission.selftext)
            embed.set_image(url=url)
            await ctx.send(embed=embed)
            

# Handles commands related to linking subreddits and obtaining flair lists.


class Reddit_Subs(commands.Cog, name="Reddit Subreddit Functionality"):
    """flrlist, link, unlink"""

    def __init__(self, bot):
        self.bot = bot

    # Mainly to help with searching.

    @commands.command(name="flrlist", help="Returns available flairs from subreddit.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def flairlist(self, ctx, sub):
        subreddit = await sub_check(sub)
        if not subreddit:
            await ctx.send("Subreddit does not exist.")
            return

        lst = {}
        datacheck = db.execute("SELECT DISTINCT flair FROM flairlist WHERE subreddit = ?", sub)

        if not datacheck:
            async for submission in subreddit.top(limit=100):
                lst[submission.link_flair_text] = submission.link_flair_text

            for flair in lst:
                await ctx.send(f"``{lst[flair]}``")
                db.execute("INSERT INTO flairlist(subreddit, flair) VALUES(?, ?)", sub, lst[flair])
        else:
            for flair2 in datacheck: 
                await ctx.send(f"``{flair2['flair']}``")

    # The next two pair of commands help bring your reddit feed to your discord server.

    @commands.command(name="link", help="Links current channel with a subreddit, sending a specified number of random, rising posts.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def link(self, ctx, sub, num: int):
        if not sub_check(sub):
            await ctx.send("Subreddit does not exist.")
            return

        intvlist = db.execute("SELECT * FROM interval_list")
        if intvlist:
            for subs in intvlist:
                if sub in subs["sub"]:
                    await ctx.send(f"Sorry, this subreddit's already been requested by {subs['user']} in channel id: {subs['channel_id']}")
                    return

        user = ctx.author
        db.execute("INSERT INTO interval_list(sub, user, id, channel_id, num) VALUES(?, ?, ?, ?, ?)",
                   sub, user.name + "#" + user.discriminator, user.id, ctx.channel.id, num)
        await ctx.send("Successfully linked subreddit to channel. Random posts from this subreddit and others linked to this channel will be sent ever half hour.")

    @commands.command(name="unlink", help="Unlinks subreddit from current channel. Only the user who linked can remove it.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def unlink(self, ctx, sub):
        linklist = db.execute("SELECT * FROM interval_list WHERE channel_id = ?", ctx.channel.id)
        if not linklist:
            await ctx.send("Error. This subreddit is either not linked to this channel or it's not in the list.")
            return

        for subs in linklist:
            if sub in subs["sub"]:
                db.execute("DELETE FROM interval_list WHERE sub = ?", sub)
                await ctx.send(f"Successfully unlinked {sub}.")

    @commands.command(name='list', help="Lists linked subreddits to current channel.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def linklist(self, ctx):
        lst = db.execute("SELECT * FROM interval_list WHERE channel_id = ?", ctx.channel.id)
        if not lst:
            await ctx.send("No subreddits linked.")
            return
        for subs in lst:
            embed = discord.Embed(title="Links")
            embed.add_field(name=subs["sub"], value=subs["user"])
        await ctx.send(embed=embed)
# Ensures that valid sub names are input.


async def sub_check(sub):
    subreddit_name = sub
    if subreddit_name.startswith(('/r/', 'r/')):
        subreddit_name = subreddit_name.split('r/')[-1]
    try:
        subreddit = await reddit.subreddit(subreddit_name, fetch=True)
        return subreddit
    except asyncprawcore.Redirect: 
        # Reddit will redirect to reddit.com/search if the subreddit doesn't exist
        return 0

# Finally, runs the bot.


bot.add_cog(Reddit_Subs(bot))
bot.add_cog(Reddit_Srch(bot))
bot.run(TOKEN)