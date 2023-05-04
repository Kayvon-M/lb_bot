import datetime
import discord
import json

from discord import app_commands

from source.core.utils.elo_utils import getNewRatings
from source.data.api.lb.lb_api import LBApi
from source.data.models.base_models import ChallengeModel, LBModeratorModel, LBUserModel, LBUserModelFromJSON
from source.data.services.tinydb.tinydb_service import TinyDBService
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
    # await ctx.response.defer()
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
# await ctx.response.defer()
# newRatings = getNewRatings(challenger, challenged, result)
async def elo_test(ctx, challenger: int, challenged: int, result: app_commands.Choice[str]):
    await ctx.response.defer()
    newRatings = getNewRatings(challenger, challenged, result.value)
    await ctx.followup.send(content="New ratings: " + str(newRatings))


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
    await ctx.response.defer()
    try:
        leadebords = []
        if mw2.value == 1:
            leadebords.append("mw2")
        if bo2.value == 1:
            leadebords.append("bo2")
        if mwii.value == 1:
            leadebords.append("mwii")
        users = dbService.getLeaderboardUsersData()
        if list(filter(lambda userData: LBUserModelFromJSON(userData).username == username, users)) == []:
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
            await ctx.followup.send(content="Added " + str(user) + " to the database.")
        else:
            await ctx.followup.send(content="User already exists in the database.")
    except Exception as e:
        await ctx.followup.send(content="Could not add user to the database.\nReason: " + str(e))


@tree.command(name="change-user-elo", description="Change User Elo.", guild=discord.Object(id=config['guildId']))
@app_commands.choices(leaderboard=[
    app_commands.Choice(name="MW2", value="mw2"),
    app_commands.Choice(name="BO2", value="bo2"),
    app_commands.Choice(name="MWII", value="mwii")
])
async def change_user_elo(ctx, user: discord.User, leaderboard: app_commands.Choice[str], elo: int):
    await ctx.response.defer()
    try:
        updatedString = dbService.updateLeaderboardUserElo(
            user.id, leaderboard.value, elo)
        await ctx.followup.send(content=updatedString)
    except Exception as e:
        await ctx.followup.send(content="Could not change user elo.\nReason: " + str(e))


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
    await ctx.response.defer()
    try:
        leadebords = []
        if mw2.value == 1:
            leadebords.append("mw2")
        if bo2.value == 1:
            leadebords.append("bo2")
        if mwii.value == 1:
            leadebords.append("mwii")
        users = dbService.getLeaderboardUsersData()
        if list(filter(lambda userData: LBUserModelFromJSON(userData).username == username, users)) == []:
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
            await ctx.followup.send(content="Added " + str(user) + " to the database.")
        else:
            await ctx.followup.send(content="User already exists in the database.")
    except Exception as e:
        await ctx.followup.send(content="Could not add user to the database.\nReason: " + str(e))


@tree.command(name="get-lb-user", description="Get Player from a Leaderboard.", guild=discord.Object(id=config['guildId']))
async def get_lb_user(ctx, user: discord.User):
    await ctx.response.defer()
    try:
        user = dbService.getLeaderboardUser(user.id)
        await ctx.followup.send(content="Found " + str(user))
    except Exception as e:
        await ctx.followup.send(content="Could not find user.")


@tree.command(name="remove-lb-user", description="Remove Player from a Leaderboard.", guild=discord.Object(id=config['guildId']))
async def remove_lb_user(ctx, user: discord.User):
    await ctx.response.defer()
    try:
        userString = dbService.removeLeaderboardUser(user.id)
        await ctx.followup.send(content=userString)
    except Exception as e:
        await ctx.followup.send(content="Could not find user.")


@tree.command(name="list-lb-users", description="List Leaderboard Users.", guild=discord.Object(id=config['guildId']))
async def list_lb_users(ctx):
    await ctx.response.defer()
    usersString = dbService.getLeaderboardUsers()
    if usersString != "":
        await ctx.followup.send(content=str(usersString))
    else:
        await ctx.followup.send(content="Could not find any players.")


@tree.command(name="list-users-lb", description="List a Leaderboard's Users.", guild=discord.Object(id=config['guildId']))
@app_commands.choices(leaderboard=[
    app_commands.Choice(name="MW2", value="mw2"),
    app_commands.Choice(name="BO2", value="bo2"),
    app_commands.Choice(name="MWII", value="mwii")
])
async def list_users_lb(ctx, leaderboard: app_commands.Choice[str]):
    await ctx.response.defer()
    usersString = dbService.getLeaderboardUsersByLeaderboard(leaderboard.value)
    if usersString != "":
        await ctx.followup.send(content=str(usersString))
    else:
        await ctx.followup.send(content="Could not find any players.")


@tree.command(name="list-users-lb-ranked", description="List a Leaderboard's Ranked Users ranked by ELO.", guild=discord.Object(id=config['guildId']))
@app_commands.choices(leaderboard=[
    app_commands.Choice(name="MW2", value="mw2"),
    app_commands.Choice(name="BO2", value="bo2"),
    app_commands.Choice(name="MWII", value="mwii")
])
async def list_users_lb_ranked(ctx, leaderboard: app_commands.Choice[str]):
    await ctx.response.defer()
    usersData = dbService.getLeaderboardUsersDataByLeaderboard(
        leaderboard.value)
    if usersData != []:
        users = list(
            map(lambda userData: LBUserModelFromJSON(userData), usersData))
        usersString = ""
        if leaderboard.value == "mw2":
            users.sort(key=lambda user: user.mw2Elo, reverse=True)
            for i in range(len(users)):
                usersString += str(i + 1) + ". " + \
                    str(users[i].username) + " " + str(users[i].mw2Elo) + "\n"
            await ctx.followup.send(content=usersString)
        elif leaderboard.value == "bo2":
            users.sort(key=lambda user: user.bo2Elo, reverse=True)
            for i in range(len(users)):
                usersString += str(i + 1) + ". " + \
                    str(users[i].username) + " " + str(users[i].bo2Elo) + "\n"
            await ctx.followup.send(content=usersString)
        elif leaderboard.value == "mwii":
            users.sort(key=lambda user: user.mwiiElo, reverse=True)
            for i in range(len(users)):
                usersString += str(i + 1) + ". " + \
                    str(users[i].username) + " " + str(users[i].mwiiElo) + "\n"
            await ctx.followup.send(content=usersString)
    else:
        await ctx.followup.send(content="Could not find any players.")


@tree.command(name="get-num-lb-users", description="Get Number of Leaderboard Users.", guild=discord.Object(id=config['guildId']))
async def get_num_lb_users(ctx):
    await ctx.response.defer()
    numUsers = dbService.getLeaderboardUserCount()
    await ctx.followup.send(content="There are " + str(numUsers) + " lb users in the database.")


@tree.command(name="get-lb-num-users", description="Get Number of Leaderboard Users.", guild=discord.Object(id=config['guildId']))
@app_commands.choices(leaderboard=[
    app_commands.Choice(name="MW2", value="mw2"),
    app_commands.Choice(name="BO2", value="bo2"),
    app_commands.Choice(name="MWII", value="mwii")
])
async def get_lb_num_users(ctx, leaderboard: app_commands.Choice[str]):
    await ctx.response.defer()
    numUsers = dbService.getLeaderboardUserCountByLeaderboard(
        leaderboard.value)
    await ctx.followup.send(content="There are " + str(numUsers) + " " + leaderboard.value + " lb users in the database.")


@tree.command(name="get-lb-user-pending", description="Get Player's Pending Challenges.", guild=discord.Object(id=config['guildId']))
async def get_lb_user_pending(ctx, user: discord.User):
    await ctx.response.defer()
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
        await ctx.followup.send(content="\n".join([f"Found {str(challenge)}" for challenge in pendingChallengesObjs]))
    except Exception as e:
        await ctx.followup.send(content="Could not find any pending challenges for " + str(user.name) + ".\nReason: " + str(e))
    # await ctx.followup.send(content="Found:\n" + "\n".join([f"\t{str(challenge)}" for challenge in pendingChallenges]))


@client.event
async def on_reaction_add(reaction, user):
    # await ctx.response.defer()
    category = client.get_channel(config["challengeCategoryId"])
    channel = reaction.message.channel
    challengerName = str(channel.name).split("-vs-")[0]
    challengedName = str(channel.name).split("-vs-")[1]
    challengerUserData = dbService.getLeaderboardUserDataByUsername(
        challengerName)
    challengedUserData = dbService.getLeaderboardUserDataByUsername(
        challengedName)
    challengerObj = LBUserModelFromJSON(challengerUserData)
    challengedObj = LBUserModelFromJSON(challengedUserData)
    # challengerChallenge = list(filter(lambda x: x.challenger.id ==
    #                            challengerObj.id and x.challenged.id == challengedObj.id, challengerObj.pendingChallenges))[0]
    # challengedChallenge = list(filter(lambda x: x.challenger.id ==
    #    challengerObj.id and x.challenged.id == challengedObj.id, challengedObj.pendingChallenges))[0]
    # try:
    if channel.category_id == category.id:
        if user.id != client.user.id and user.id == challengedObj.id:
            if reaction.emoji == "✅":
                await reaction.message.delete()
                await channel.send("Challenge Accepted!")
                challengerChallenges = dbService.getLeaderboardUserPendingChallenges(
                    challengerObj.id)
                challengedChallenges = dbService.getLeaderboardUserPendingChallenges(
                    challengedObj.id)
                challengerChallenge = list(filter(
                    lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengerChallenges))[0]
                challengedChallenge = list(filter(
                    lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengedChallenges))[0]
                lbApi.acceptChallenge(challengerChallenge)
                # lbApi.acceptChallenge(challengedChallenge)
            elif reaction.emoji == "❌":
                await reaction.message.delete()
                await channel.send("Challenge Declined!")
                challengerChallenges = dbService.getLeaderboardUserPendingChallenges(
                    challengerObj.id)
                challengedChallenges = dbService.getLeaderboardUserPendingChallenges(
                    challengedObj.id)
                challengerChallenge = list(filter(
                    lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengerChallenges))[0]
                challengedChallenge = list(filter(
                    lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengedChallenges))[0]
                lbApi.declineChallenge(challengerChallenge)
                # lbApi.declineChallenge(challengedChallenge)
        elif user.id != client.user.id and user.id != challengedObj.id:
            await reaction.message.remove_reaction(reaction.emoji, user)
    # except Exception as e:
    #     await channel.send("Could not find a challenge for " + str(user) + ".\nReason: " + str(e))


@tree.command(name="lb-challenge", description="Challenge a Player from a Leaderboard.", guild=discord.Object(id=config['guildId']))
@app_commands.choices(leaderboard=[
    app_commands.Choice(name="MW2", value="mw2"),
    app_commands.Choice(name="BO2", value="bo2"),
    app_commands.Choice(name="MWII", value="mwii")
])
async def lb_challenge(ctx, challenged: discord.User, leaderboard: app_commands.Choice[str]):
    await ctx.response.defer()
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
        await ctx.followup.send(content="Challenge created: " + str(challenge) + "\n" + "Channel created: " + channel.mention)
    except Exception as e:
        await ctx.followup.send(content="Could not create challenge.\nReason: " + str(e))


@tree.command(name="lb-rm-active-challenge", description="Remove a Challenge from a user's active challenges.", guild=discord.Object(id=config['guildId']))
async def lb_rm_active_challenge(ctx, user: discord.User, cid: str):
    await ctx.response.defer()
    try:
        removedStr = dbService.removeChallengeFromLeaderboardUserActiveChallenges(
            user.id, int(cid))
        await ctx.followup.send(content=removedStr)
    except Exception as e:
        await ctx.followup.send(content="Could not remove challenge.\nReason: " + str(e))


@tree.command(name="get-lb-user-active", description="Get a user's active challenges.", guild=discord.Object(id=config['guildId']))
async def get_lb_user_active(ctx, user: discord.User):
    await ctx.response.defer()
    try:
        activeChallenges = dbService.getLeaderboardUserActiveChallengesById(
            user.id)
        await ctx.followup.send(content="Found:\n" + str(activeChallenges))
    except Exception as e:
        await ctx.followup.send(content="Could not find any active challenges for " + str(user) + ".\nReason: " + str(e))


@tree.command(name="lb-rm-challenge", description="Remove a Challenge from a user's pending challenges.", guild=discord.Object(id=config['guildId']))
async def lb_rm_challenge(ctx, user: discord.User, cid: str):
    await ctx.response.defer()
    try:
        newChallengeId = int(cid)
        challenge = lbApi.removeChallengeFromLBUserPendingChallenges(
            user.id, newChallengeId)
        await ctx.followup.send(content="Challenge removed: " + challenge)
    except Exception as e:
        await ctx.followup.send(content="Could not remove challenge.\nReason: " + str(e))


@tree.command(name="lb-rm-all-challenges", description="Remove all Challenges from a user's pending challenges.", guild=discord.Object(id=config['guildId']))
async def lb_rm_all_challenges(ctx, user: discord.User):
    await ctx.response.defer()
    try:
        challenges = lbApi.removeAllChallengesFromLBUserPendingChallenges(
            user.id)
        await ctx.followup.send(content="Challenges removed: " + str(challenges))
    except Exception as e:
        await ctx.followup.send(content="Could not remove challenges.\nReason: " + str(e))


@tree.command(name="create-text-channel", description="Create a Text Channel.", guild=discord.Object(id=config['guildId']))
@app_commands.choices(leaderboard=[
    app_commands.Choice(name="MW2", value="mw2"),
    app_commands.Choice(name="BO2", value="bo2"),
    app_commands.Choice(name="MWII", value="mwii")
])
async def create_text_channel(ctx, name: str, challenger: discord.User, challenged: discord.User, leaderboard: str):
    await ctx.response.defer()
    # try:
    channel = await ctx.guild.create_text_channel(name)
    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await channel.set_permissions(challenger, send_messages=True)
    await channel.set_permissions(challenged, send_messages=True)
    admins = dbService.getLeaderboardModeratorsData()
    for admin in admins:
        await channel.set_permissions(client.get_user(admin["id"]), send_messages=True)
    await channel.send(content=f"{challenger.mention} has challenged {challenged.mention} to a {leaderboard} match!")
    await ctx.followup.send(content="Channel created: " + channel.mention)
    # except Exception as e:
    #     await ctx.followup.send(content="Could not create channel.\nReason: " + str(e))


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
    await ctx.response.defer()
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
    await ctx.followup.send(content="Added " + str(user) + " to the database.")


@tree.command(name="get-mod-user", description="Get Moderator User.", guild=discord.Object(id=config['guildId']))
async def get_mod_user(ctx, user: discord.User):
    await ctx.response.defer()
    try:
        user = dbService.getLeaderboardModerator(user.id)
        await ctx.followup.send(content="Found " + str(user))
    except Exception as e:
        await ctx.followup.send(content="Could not find user.")


@tree.command(name="remove-mod-user", description="Remove Moderator User.", guild=discord.Object(id=config['guildId']))
async def remove_mod_user(ctx, user: discord.User):
    await ctx.response.defer()
    try:
        userString = dbService.removeLeaderboardModerator(user.id)
        await ctx.followup.send(content=userString)
    except Exception as e:
        await ctx.followup.send(content="Could not find user.")


@tree.command(name="list-mod-users", description="List Moderator Users.", guild=discord.Object(id=config['guildId']))
async def list_mod_users(ctx):
    await ctx.response.defer()
    usersString = dbService.getLeaderboardModerators()
    if usersString != "":
        await ctx.followup.send(content=str(usersString))
    else:
        await ctx.followup.send(content="Could not find any moderators.")

client.run(config['token'])
