import discord
import random
import time
import yaml
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Load config from config.yml
with open('config.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)

# Load compliments from config
compliments = config['compliments']

# Load keyword-response mappings from config
keyword_responses = config.get('trigger_keywords', {})

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def compliment(ctx, user: discord.User):
    compliment_text = random.choice(compliments)
    await user.send(compliment_text)
    await ctx.send(f'Compliment sent to {user.name}')

@tasks.loop(minutes=10)
async def random_compliments():
    guild = bot.get_guild(config['guild_id'])
    if guild:
        channel = guild.get_channel(config['random_compliments_channel_id'])
        if channel:
            random_user = random.choice(guild.members)
            compliment_text = random.choice(compliments)
            await random_user.send(compliment_text)
            await channel.send(f'Sent a compliment to {random_user.mention}.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content_lower = message.content.lower()
    for keyword, response in keyword_responses.items():
        if keyword in content_lower:
            await message.channel.send(response)

    await bot.process_commands(message)

# Debugging/Admin Commands
@bot.command()
async def ping(ctx):
    """Responds with the bot's latency."""
    latency = bot.latency
    await ctx.send(f'Pong! Latency: {latency:.2f}ms')

@bot.command()
async def echo(ctx, *, text):
    """Echoes back the provided text."""
    await ctx.send(text)

@bot.command()
async def serverinfo(ctx):
    """Displays information about the server."""
    guild = ctx.guild
    member_count = len(guild.members)
    online_members = sum(1 for member in guild.members if member.status == discord.Status.online)
    await ctx.send(f'Server: {guild.name}\nTotal Members: {member_count}\nOnline Members: {online_members}')

@bot.command()
async def userinfo(ctx, user: discord.User = None):
    """Displays information about the mentioned user or yourself."""
    user = user or ctx.author
    user_info = f'User: {user.name}\nID: {user.id}\nStatus: {user.status}\nJoined Server: {user.joined_at}'
    await ctx.send(user_info)

@bot.command()
async def listmembers(ctx):
    """Lists all members in the server."""
    members = '\n'.join(member.name for member in ctx.guild.members)
    await ctx.send(f'Members in this server:\n{members}')

@bot.command()
async def randomuser(ctx):
    """Mentions a random user in the server."""
    random_member = random.choice(ctx.guild.members)
    await ctx.send(f'Random user: {random_member.mention}')

@bot.command()
async def avatar(ctx, user: discord.User = None):
    """Displays the avatar of the mentioned user or yourself."""
    user = user or ctx.author
    avatar_url = user.avatar_url
    await ctx.send(f'Avatar of {user.name}: {avatar_url}')

@bot.command()
async def listchannels(ctx):
    """Lists all text channels in the server."""
    channels = '\n'.join(channel.name for channel in ctx.guild.text_channels)
    await ctx.send(f'Text channels in this server:\n{channels}')

@bot.command()
async def botinfo(ctx):
    """Displays information about the bot."""
    bot_info = f'Bot Name: {bot.user.name}\nID: {bot.user.id}\nPrefix: {bot.command_prefix}'
    await ctx.send(bot_info)

# Additional Debugging/Admin Commands
@bot.command()
async def version(ctx):
    """Displays the bot's current version."""
    bot_version = config.get('bot_version', 'Unknown')
    await ctx.send(f'Bot Version: {bot_version}')

@bot.command()
async def uptime(ctx):
    """Displays the bot's uptime."""
    uptime = time.time() - bot.start_time
    await ctx.send(f'Uptime: {uptime:.2f} seconds')

@bot.command()
async def invite(ctx):
    """Provides an invite link for the bot."""
    await ctx.send('Invite link: https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&scope=bot&permissions=YOUR_PERMISSIONS')

@bot.command()
async def github(ctx):
    """Provides a link to the bot's GitHub repository."""
    github_repo = config.get('github_repo', 'Unknown')
    await ctx.send(f'GitHub Repository: {github_repo}')

# Set the bot's start time
bot.start_time = time.time()

# Run the bot using the correct token from the config
bot_token = config['bot_token']
bot.run(bot_token)
