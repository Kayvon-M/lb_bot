import datetime
import discord
import json

from discord import app_commands

from source.core.utils.elo_utils import getNewRatings
from source.data.api.lb.lb_api import LBApi
from source.data.models.base_models import ChallengeModel, LBModeratorModel, LBUserModel, LBUserModelFromJSON
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
lbApi = LBApi()

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
    users = dbService.getLeaderboardUsersData()
    if list(filter(lambda userData: LBUserModelFromJSON(userData).id == user.id, users)) == []:
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
    else:
        await ctx.response.send_message(content="User already exists in the database.")


@tree.command(name="lb-register", description="Register for Leaderboard(s)", guild=discord.Object(id=config['guildId']))
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
async def lb_register(ctx, username: str, mw2: app_commands.Choice[int], bo2: app_commands.Choice[int], mwii: app_commands.Choice[int]):
    leadebords = []
    if mw2.value == 1:
        leadebords.append("mw2")
    if bo2.value == 1:
        leadebords.append("bo2")
    if mwii.value == 1:
        leadebords.append("mwii")
    userFound = dbService.getLeaderboardUser(ctx.user.id)
    if userFound is None:
        user = LBUserModel(
            id=ctx.user.id,
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
    else:
        await ctx.response.send_message(content="You are already registered.")


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


@tree.command(name="list-users-lb", description="List a Leaderboard's Users.", guild=discord.Object(id=config['guildId']))
@app_commands.choices(leaderboard=[
    app_commands.Choice(name="MW2", value="mw2"),
    app_commands.Choice(name="BO2", value="bo2"),
    app_commands.Choice(name="MWII", value="mwii")
])
async def list_users_lb(ctx, leaderboard: app_commands.Choice[str]):
    usersString = dbService.getLeaderboardUsersByLeaderboard(leaderboard.value)
    if usersString != "":
        await ctx.response.send_message(content=str(usersString))
    else:
        await ctx.response.send_message(content="Could not find any players.")


@tree.command(name="get-num-lb-users", description="Get Number of Leaderboard Users.", guild=discord.Object(id=config['guildId']))
async def get_num_lb_users(ctx):
    numUsers = dbService.getLeaderboardUserCount()
    await ctx.response.send_message(content="There are " + str(numUsers) + " lb users in the database.")


@tree.command(name="get-lb-num-users", description="Get Number of Leaderboard Users.", guild=discord.Object(id=config['guildId']))
@app_commands.choices(leaderboard=[
    app_commands.Choice(name="MW2", value="mw2"),
    app_commands.Choice(name="BO2", value="bo2"),
    app_commands.Choice(name="MWII", value="mwii")
])
async def get_lb_num_users(ctx, leaderboard: app_commands.Choice[str]):
    numUsers = dbService.getLeaderboardUserCountByLeaderboard(
        leaderboard.value)
    await ctx.response.send_message(content="There are " + str(numUsers) + " " + leaderboard.value + " lb users in the database.")


@tree.command(name="get-lb-user-pending", description="Get Player's Pending Challenges.", guild=discord.Object(id=config['guildId']))
async def get_lb_user_pending(ctx, user: discord.User):
    try:
        pendingChallenges = dbService.getLeaderboardUserPendingChallenges(
            user.id)
        pendingChallengesObjs = []
        for challenge in pendingChallenges:
            challengeObj = ChallengeModel(
                id=challenge["id"],
                challengeTime=challenge["challengeTime"],
                challenger=LBUserModel(
                    id=challenge["challenger"]['id'],
                    username=challenge["challenger"]['username'],
                    isBanned=challenge["challenger"]['isBanned'],
                    isModerator=challenge["challenger"]['isModerator'],
                    leaderboards=challenge["challenger"]['leaderboards'],
                    joinDate=challenge["challenger"]['joinDate'],
                    lastActiveDate=challenge["challenger"]['lastActiveDate'],
                    mw2Elo=challenge["challenger"]['mw2Elo'],
                    bo2Elo=challenge["challenger"]['bo2Elo'],
                    mwiiElo=challenge["challenger"]['mwiiElo'],
                    matchHistory=challenge["challenger"]['matchHistory'],
                    activeChallenges=challenge["challenger"]['activeChallenges'],
                    pendingChallenges=challenge["challenger"]['pendingChallenges'],
                    challengeHistory=challenge["challenger"]['challengeHistory'],
                    moderationHistory=challenge["challenger"]['moderationHistory'],
                ),
                challenged=LBUserModel(
                    id=challenge["challenged"]['id'],
                    username=challenge["challenged"]['username'],
                    isBanned=challenge["challenged"]['isBanned'],
                    isModerator=challenge["challenged"]['isModerator'],
                    leaderboards=challenge["challenged"]['leaderboards'],
                    joinDate=challenge["challenged"]['joinDate'],
                    lastActiveDate=challenge["challenged"]['lastActiveDate'],
                    mw2Elo=challenge["challenged"]['mw2Elo'],
                    bo2Elo=challenge["challenged"]['bo2Elo'],
                    mwiiElo=challenge["challenged"]['mwiiElo'],
                    matchHistory=challenge["challenged"]['matchHistory'],
                    activeChallenges=challenge["challenged"]['activeChallenges'],
                    pendingChallenges=challenge["challenged"]['pendingChallenges'],
                    challengeHistory=challenge["challenged"]['challengeHistory'],
                    moderationHistory=challenge["challenged"]['moderationHistory'],
                ),
                leaderboard=challenge["leaderboard"],
                isAccepted=challenge["isAccepted"],
                isMandatory=challenge["isMandatory"],
                expiryTime=challenge["expiryTime"],
                result=challenge["result"],
            )
            pendingChallengesObjs.append(challengeObj)
        if len(pendingChallengesObjs) == 0:
            raise Exception("No pending challenges found.")
        await ctx.response.send_message(content="\n".join([f"Found {str(challenge)}" for challenge in pendingChallengesObjs]))
    except Exception as e:
        await ctx.response.send_message(content="Could not find any pending challenges for " + str(user) + ".\nReason: " + str(e))
    # await ctx.response.send_message(content="Found:\n" + "\n".join([f"\t{str(challenge)}" for challenge in pendingChallenges]))


@client.event
async def on_reaction_add(reaction, user):
    # print("reaction added")
    category = client.get_channel(config["challengeCategoryId"])
    channel = reaction.message.channel
    challengedName = str(channel.name).split("-vs-")[1]
    try:
        challengedUserData = dbService.getLeaderboardUserDataByUsername(
            challengedName)
        challengedObj = LBUserModelFromJSON(challengedUserData)
        # print(challengedObj)
        if channel.category_id == category.id:
            if user.id != client.user.id and reaction.message.author.id == challengedObj.id:
                if reaction.emoji == "✅":
                    await reaction.message.delete()
                    await channel.send("Challenge Accepted!")
                    # await lbApi.acceptChallenge(channel.name)
                elif reaction.emoji == "❌":
                    await reaction.message.delete()
                    await channel.send("Challenge Declined!")
                    # await lbApi.declineChallenge(channel.name)
            elif user.id != client.user.id and reaction.message.author.id != challengedObj.id:
                await reaction.message.remove_reaction(reaction.emoji, user)
    except Exception as e:
        await channel.send("Could not find a challenge for " + str(user) + ".\nReason: " + str(e))


@tree.command(name="lb-challenge", description="Challenge a Player from a Leaderboard.", guild=discord.Object(id=config['guildId']))
@app_commands.choices(leaderboard=[
    app_commands.Choice(name="MW2", value="mw2"),
    app_commands.Choice(name="BO2", value="bo2"),
    app_commands.Choice(name="MWII", value="mwii")
])
async def lb_challenge(ctx, challenged: discord.User, leaderboard: app_commands.Choice[str]):
    try:
        challenge = lbApi.challengeLBUser(
            ctx.user.id, challenged.id, leaderboard.value)
        category = client.get_channel(config["challengeCategoryId"])
        channel = await category.create_text_channel(str(challenge.challenger.username).lower() + "-vs-" + str(challenge.challenged.username).lower())
        await channel.set_permissions(ctx.guild.default_role, send_messages=False, add_reactions=False)
        await channel.set_permissions(ctx.user, send_messages=True, add_reactions=True)
        await channel.set_permissions(challenged, send_messages=True, add_reactions=True)
        admins = dbService.getLeaderboardModeratorsData()
        for admin in admins:
            await channel.set_permissions(client.get_user(admin["id"]), send_messages=True, add_reactions=False)
        message = await channel.send(content=f"{ctx.user.mention} has challenged {challenged.mention} to a {leaderboard.value} match!")
        reactions = ["✅", "❌"]
        for reaction in reactions:
            await message.add_reaction(reaction)
        await ctx.response.send_message(content="Challenge created: " + str(challenge) + "\n" + "Channel created: " + channel.mention)
    except Exception as e:
        await ctx.response.send_message(content="Could not create challenge.\nReason: " + str(e))


@tree.command(name="lb-rm-challenge", description="Remove a Challenge from a user's pending challenges.", guild=discord.Object(id=config['guildId']))
async def lb_rm_challenge(ctx, user: discord.User, cid: str):
    try:
        newChallengeId = int(cid)
        challenge = lbApi.removeChallengeFromLBUserPendingChallenges(
            user.id, newChallengeId)
        await ctx.response.send_message(content="Challenge removed: " + challenge)
    except Exception as e:
        await ctx.response.send_message(content="Could not remove challenge.\nReason: " + str(e))


@tree.command(name="lb-rm-all-challenges", description="Remove all Challenges from a user's pending challenges.", guild=discord.Object(id=config['guildId']))
async def lb_rm_all_challenges(ctx, user: discord.User):
    try:
        challenges = lbApi.removeAllChallengesFromLBUserPendingChallenges(
            user.id)
        await ctx.response.send_message(content="Challenges removed: " + str(challenges))
    except Exception as e:
        await ctx.response.send_message(content="Could not remove challenges.\nReason: " + str(e))


@tree.command(name="create-text-channel", description="Create a Text Channel.", guild=discord.Object(id=config['guildId']))
@app_commands.choices(leaderboard=[
    app_commands.Choice(name="MW2", value="mw2"),
    app_commands.Choice(name="BO2", value="bo2"),
    app_commands.Choice(name="MWII", value="mwii")
])
async def create_text_channel(ctx, name: str, challenger: discord.User, challenged: discord.User, leaderboard: str):
    # try:
    channel = await ctx.guild.create_text_channel(name)
    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await channel.set_permissions(challenger, send_messages=True)
    await channel.set_permissions(challenged, send_messages=True)
    admins = dbService.getLeaderboardModeratorsData()
    for admin in admins:
        await channel.set_permissions(client.get_user(admin["id"]), send_messages=True)
    await channel.send(content=f"{challenger.mention} has challenged {challenged.mention} to a {leaderboard} match!")
    await ctx.response.send_message(content="Channel created: " + channel.mention)
    # except Exception as e:
    #     await ctx.response.send_message(content="Could not create channel.\nReason: " + str(e))


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
