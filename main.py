import datetime
import discord
import json

from discord import app_commands

from source.core.utils.elo_utils import getNewRatings
from source.data.models.base_models import LBModeratorModel, LBUserModel
from source.data.models.services.tinydb.tinydb_service import TinyDBService
from source.core.utils.time_utils import getNowAsStr

# Load config
with open('source/config/config.json') as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Initialize tinydb
dbService = TinyDBService()

print(dbService.getLeaderboardUsers())


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(config['guildId']))

    activeChannel = client.get_channel(config['activeChannelId'])
    await activeChannel.send(content="Bot is ready.")
    print("Bot is ready.")


@tree.command(name="elo-test", description="Test elo calculation.", guild=discord.Object(id=config['guildId']))
@app_commands.choices(result=[
    app_commands.Choice(name="Win", value="win"),
    app_commands.Choice(name="Loss", value="loss"),
    app_commands.Choice(name="Draw", value="draw"),
    app_commands.Choice(name="DQ", value="dq")
])
# async def elo_test(ctx, challenger: discord.User, challenged: discord.User, result: str):
# newRatings = getNewRatings(challenger, challenged, result)
async def elo_test(ctx, challenger: int, challenged: int, result: app_commands.Choice[str]):
    newRatings = getNewRatings(challenger, challenged, result.value)
    await ctx.response.send_message(content="New ratings: " + str(newRatings))


@tree.command(name="add-lb-user", description="Add Player to a Leaderboard.", guild=discord.Object(id=config['guildId']))
@app_commands.choices(mw2=[
    app_commands.Choice(name="Playing", value=1),
    app_commands.Choice(name="Not Playing", value=0)
])
@app_commands.choices(bo2=[
    app_commands.Choice(name="Playing", value=1),
    app_commands.Choice(name="Not Playing", value=0)
])
@app_commands.choices(mwii=[
    app_commands.Choice(name="Playing", value=1),
    app_commands.Choice(name="Not Playing", value=0)
])
async def add_lb_user(ctx, user: discord.User, username: str, mw2: app_commands.Choice[int], bo2: app_commands.Choice[int], mwii: app_commands.Choice[int]):
    leadebords = []
    if mw2.value == 1:
        leadebords.append("mw2")
    if bo2.value == 1:
        leadebords.append("bo2")
    if mwii.value == 1:
        leadebords.append("mwii")
    user = LBUserModel(
        id=user.id,
        username=username,
        isBanned=False,
        isModerator=False,
        leaderboards=leadebords,
        joinDate=getNowAsStr(),
        lastActiveDate=getNowAsStr(),
        mw2Elo=500 if mw2.value == 1 else None,
        bo2Elo=500 if bo2.value == 1 else None,
        mwiiElo=500 if mwii.value == 1 else None,
        matchHistory=[],
        activeChallenges=[],
        pendingChallenges=[],
        challengeHistory=[],
        moderationHistory=[],
    )
    dbService.addLeaderboardUser(user)
    await ctx.response.send_message(content="Added " + str(user) + " to the database.")


@tree.command(name="get-lb-user", description="Get Player from a Leaderboard.", guild=discord.Object(id=config['guildId']))
async def get_lb_user(ctx, user: discord.User):
    try:
        user = dbService.getLeaderboardUser(user.id)
        await ctx.response.send_message(content="Found " + str(user))
    except Exception as e:
        await ctx.response.send_message(content="Could not find user.")


@tree.command(name="remove-lb-user", description="Remove Player from a Leaderboard.", guild=discord.Object(id=config['guildId']))
async def remove_lb_user(ctx, user: discord.User):
    try:
        userString = dbService.removeLeaderboardUser(user.id)
        await ctx.response.send_message(content=userString)
    except Exception as e:
        await ctx.response.send_message(content="Could not find user.")


@tree.command(name="list-lb-users", description="List Leaderboard Users.", guild=discord.Object(id=config['guildId']))
async def list_lb_users(ctx):
    usersString = dbService.getLeaderboardUsers()
    if usersString != "":
        await ctx.response.send_message(content=str(usersString))
    else:
        await ctx.response.send_message(content="Could not find any players.")


@tree.command(name="add-mod-user", description="Add Moderator User.", guild=discord.Object(id=config['guildId']))
@ app_commands.choices(mw2=[
    app_commands.Choice(name="Moderator", value=1),
    app_commands.Choice(name="Not Moderator", value=0)
])
@ app_commands.choices(bo2=[
    app_commands.Choice(name="Moderator", value=1),
    app_commands.Choice(name="Not Moderator", value=0)
])
@ app_commands.choices(mwii=[
    app_commands.Choice(name="Moderator", value=1),
    app_commands.Choice(name="Not Moderator", value=0)
])
async def add_mod_user(ctx, user: discord.User, username: str, mw2: app_commands.Choice[int], bo2: app_commands.Choice[int], mwii: app_commands.Choice[int]):
    leadebords = []
    if mw2.value == 1:
        leadebords.append("mw2")
    if bo2.value == 1:
        leadebords.append("bo2")
    if mwii.value == 1:
        leadebords.append("mwii")
    user = LBModeratorModel(
        id=user.id,
        username=username,
        isBanned=False,
        isModerator=True,
        leaderboards=leadebords,
        joinDate=getNowAsStr(),
        lastActiveDate=getNowAsStr(),
        moderationHistory=[],
    )
    dbService.addLeaderboardModerator(user)
    await ctx.response.send_message(content="Added " + str(user) + " to the database.")


@tree.command(name="get-mod-user", description="Get Moderator User.", guild=discord.Object(id=config['guildId']))
async def get_mod_user(ctx, user: discord.User):
    try:
        user = dbService.getLeaderboardModerator(user.id)
        await ctx.response.send_message(content="Found " + str(user))
    except Exception as e:
        await ctx.response.send_message(content="Could not find user.")


@tree.command(name="remove-mod-user", description="Remove Moderator User.", guild=discord.Object(id=config['guildId']))
async def remove_mod_user(ctx, user: discord.User):
    try:
        userString = dbService.removeLeaderboardModerator(user.id)
        await ctx.response.send_message(content=userString)
    except Exception as e:
        await ctx.response.send_message(content="Could not find user.")


@tree.command(name="list-mod-users", description="List Moderator Users.", guild=discord.Object(id=config['guildId']))
async def list_mod_users(ctx):
    usersString = dbService.getLeaderboardModerators()
    if usersString != "":
        await ctx.response.send_message(content=str(usersString))
    else:
        await ctx.response.send_message(content="Could not find any moderators.")

client.run(config['token'])
