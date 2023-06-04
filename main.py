import asyncio
import random
import threading
import discord
import json

from discord import app_commands
# from discord.ext import commands
from datetime import datetime, timedelta
from source.core.utils.elo_utils import getNewRatings
from source.data.api.lb.lb_api import LBApi
# from source.data.api.lb.queue_api import QueueApi, setup
from source.data.models.base_models import ChallengeModel, ChallengeModelFromJSON, LBModeratorModel, LBUserModel, LBUserModelFromJSON, PendingChallengeScheduledActionGroupModel, PendingChallengeScheduledActionGroupModelFromJSON, ScheduledActionModel
from source.data.services.mongodb.mongodb_service import MongoDBService
# from source.data.services.scheduler.scheduler_service import SchedulerService
from source.data.services.tinydb.tinydb_service import TinyDBService
from source.core.utils.time_utils import getNowAsStr
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Load config
with open('source/config/config.json') as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Initialize services
# scheduler = SchedulerService()
dbService = MongoDBService()
lbApi = LBApi()
lbSchedulerDB = "lbScheduler"
scheduler = AsyncIOScheduler()
scheduler.add_jobstore('mongodb', collection=lbSchedulerDB, database="1v1lb")

def loop_in_thread(loop=None):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def add_job(func, trigger, run_date=None, args=None):
    job = scheduler.add_job(func, trigger, run_date=run_date, args=args)
    return job

def remove_job(job_id):
    scheduler.remove_job(job_id)

def get_jobs():
    return scheduler.get_jobs()

def get_job(job_id):
    return scheduler.get_job(job_id)

def get_job_ids():
    return scheduler.get_job_ids()

def get_job_id(job):
    return scheduler.get_job_id(job)

def clear():
    scheduler.remove_all_jobs()

def run_after_1_min(func, args=None):
    run_date = datetime.now() + timedelta(minutes=1)
    return add_job(func, 'date', run_date=run_date, args=args)

def delete_challenge_tc_job(func, args=None):
    run_date = datetime.now() + timedelta(minutes=1)
    return add_job(func, 'date', run_date=run_date)

def message_user_about_challenge_job(funcOne, funcTwo, funcThree, funcFour, argsOne=None, argsTwo=None, argsThree=None, argsFour=None):
    run_date = datetime.now() + timedelta(days=1)
    job_one = add_job(funcOne, 'date', run_date=run_date, args=argsOne)
    run_date = datetime.now() + timedelta(days=2)
    job_two = add_job(funcTwo, 'date', run_date=run_date, args=argsTwo)
    run_date = datetime.now() + timedelta(days=2, hours=23)
    job_three = add_job(funcThree, 'date', run_date=run_date, args=argsThree)
    run_date = datetime.now()
    job_four = add_job(funcFour, 'date', run_date=run_date, args=argsFour)
    return job_one, job_two, job_three, job_four

try:
    print(dbService.getAllLeaderboardUsersStrings())
except Exception as e:
    print(e)


async def delete_channel(channelId):
    channel = client.get_channel(channelId)
    asyncio.run_coroutine_threadsafe(channel.delete(), client.loop)


async def message_user_about_pending_match(userId, challengerObj, challengedObj, time):
    user = client.get_user(userId)
    asyncio.run_coroutine_threadsafe(user.send(content="You have a pending match with " + challengerObj.username + " and " + challengedObj.username + " in " + str(time)), client.loop)


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
        users = dbService.getAllLeaderboardUsersData()
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
            dbService.addLeaderboardUser(user.toJSON())
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
        updatedString = dbService.updateLeaderboardUserEloById(
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
        users = dbService.getAllLeaderboardUsersData()
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
            dbService.addLeaderboardUser(user.toJSON())
            await ctx.followup.send(content="Added " + str(user) + " to the database.")
        else:
            await ctx.followup.send(content="User already exists in the database.")
    except Exception as e:
        await ctx.followup.send(content="Could not add user to the database.\nReason: " + str(e))


@tree.command(name="get-lb-user", description="Get Player from a Leaderboard.", guild=discord.Object(id=config['guildId']))
async def get_lb_user(ctx, user: discord.User):
    await ctx.response.defer()
    try:
        user = dbService.getLeaderboardUserObjectById(user.id)
        await ctx.followup.send(content="Found " + str(user))
    except Exception as e:
        await ctx.followup.send(content="Could not find user.")


@tree.command(name="remove-lb-user", description="Remove Player from a Leaderboard.", guild=discord.Object(id=config['guildId']))
async def remove_lb_user(ctx, user: discord.User):
    await ctx.response.defer()
    try:
        userString = dbService.removeLeaderboardUserById(user.id)
        await ctx.followup.send(content=userString)
    except Exception as e:
        await ctx.followup.send(content="Could not find user.")


@tree.command(name="list-lb-users", description="List Leaderboard Users.", guild=discord.Object(id=config['guildId']))
async def list_lb_users(ctx):
    await ctx.response.defer()
    usersString = dbService.getAllLeaderboardUsersStrings()
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
    usersString = dbService.getLeaderboadUsersStringsByLeaderboard(leaderboard.value)
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
    usersData = dbService.getLeaderboadUsersDataByLeaderboard(
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
    numUsers = dbService.getAllLeaderboardUsersCount()
    await ctx.followup.send(content="There are " + str(numUsers) + " lb users in the database.")


@tree.command(name="get-lb-num-users", description="Get Number of Leaderboard Users.", guild=discord.Object(id=config['guildId']))
@app_commands.choices(leaderboard=[
    app_commands.Choice(name="MW2", value="mw2"),
    app_commands.Choice(name="BO2", value="bo2"),
    app_commands.Choice(name="MWII", value="mwii")
])
async def get_lb_num_users(ctx, leaderboard: app_commands.Choice[str]):
    await ctx.response.defer()
    numUsers = dbService.getLeaderboardUsersCountByLeaderboard(
        leaderboard.value)
    await ctx.followup.send(content="There are " + str(numUsers) + " " + leaderboard.value + " lb users in the database.")


@tree.command(name="get-lb-user-pending", description="Get Player's Pending Challenges.", guild=discord.Object(id=config['guildId']))
async def get_lb_user_pending(ctx, user: discord.User):
    await ctx.response.defer()
    try:
        pendingChallenges = dbService.getAllChallengeDataFromLeaderboardUserPendingChallengesById(
            user.id)
        pendingChallengesObjs = []
        for challenge in pendingChallenges:
            challengeObj = ChallengeModelFromJSON(challenge)
            pendingChallengesObjs.append("Found " + str(challengeObj))
        if len(pendingChallengesObjs) == 0:
            raise Exception("No pending challenges found.")
        await ctx.followup.send(content="\n".join(pendingChallengesObjs))
    except Exception as e:
        await ctx.followup.send(content="Could not find any pending challenges for " + str(user.name) + ".\nReason: " + str(e))


@client.event
async def on_reaction_add(reaction, user):
    # await ctx.response.defer()
    category = client.get_channel(config["challengeCategoryId"])
    channel = reaction.message.channel
    challengerName = str(channel.name).split("🔴-vs-🔵")[0]
    challengedName = str(channel.name).split("🔴-vs-🔵")[1]
    challengerUserData = dbService.getLeaderboardUserDataByName(
        challengerName.replace("-", " "))
    challengedUserData = dbService.getLeaderboardUserDataByName(
        challengedName.replace("-", " "))
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
                challengerChallenges = dbService.getAllChallengeDataFromLeaderboardUserPendingChallengesById(
                    challengerObj.id)
                challengedChallenges = dbService.getAllChallengeDataFromLeaderboardUserPendingChallengesById(
                    challengedObj.id)
                challengerChallenge = list(filter(
                    lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengerChallenges))[0]
                challengedChallenge = list(filter(
                    lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengedChallenges))[0]
                lbApi.acceptChallenge(challengerChallenge)
                whoWonReaction = await channel.send("Who won?")
                await whoWonReaction.add_reaction("🔴")
                await whoWonReaction.add_reaction("🔵")
                message_user_jobs = message_user_about_challenge_job(
                    message_user_about_pending_match,
                    message_user_about_pending_match,
                    message_user_about_pending_match,
                    message_user_about_pending_match,
                    [challengerObj.id, challengerObj, challengedObj, "2 days" ],
                    [challengerObj.id, challengerObj, challengedObj, "1 days" ],
                    [challengerObj.id, challengerObj, challengedObj, "1 hour" ],
                    [challengerObj.id, challengerObj, challengedObj, "3 days" ],
                )
                scheduledActionGroupObj = None
                try:
                    scheduledActionGroup = dbService.getPendingChallengeScheduledActionGroupObjectFromLBUser(
                        challengerObj.id, channel.name)
                except Exception as e:
                    pendingchallengeGroup = PendingChallengeScheduledActionGroupModel(
                            challengeName=channel.name,
                            challengerId=challengerObj.id,
                            challengedId=challengedObj.id,
                            actions=[]
                        ).toJSON()
                    dbService.addPendingChallengeScheduledActionGroupToLBUser(
                        challengerObj.id, pendingchallengeGroup
                    )
                    scheduledActionGroup = dbService.getPendingChallengeScheduledActionGroupObjectFromLBUser(
                        challengerObj.id, channel.name)
                print(scheduledActionGroup)
                actionsToAdd = []
                for action in message_user_jobs:
                    if action.id not in list(map(lambda x: x.id, scheduledActionGroup.actions)):
                        actionsToAdd.append(
                            ScheduledActionModel(
                                actionType="message",
                                actionId=action.id,
                                actionTime=action.next_run_time
                            ).toJSON()
                        )
                print(actionsToAdd)
                if len(actionsToAdd) > 0:
                    for action in actionsToAdd:
                        dbService.addScheduledActionToLBUserPendingChallengeScheduledActionGroup(
                            challengerObj.id, channel.name, action)
                message_user_jobs = message_user_about_challenge_job(
                    message_user_about_pending_match,
                    message_user_about_pending_match,
                    message_user_about_pending_match,
                    message_user_about_pending_match,
                    [challengedObj.id, challengerObj, challengedObj, "2 days" ],
                    [challengedObj.id, challengerObj, challengedObj, "1 days" ],
                    [challengedObj.id, challengerObj, challengedObj, "1 hour" ],
                    [challengedObj.id, challengerObj, challengedObj, "3 days" ],
                )
                scheduledActionGroupObj = None
                try:
                    scheduledActionGroup = dbService.getPendingChallengeScheduledActionGroupObjectFromLBUser(
                        challengedObj.id, channel.name)
                except Exception as e:
                    pendingchallengeGroup = PendingChallengeScheduledActionGroupModel(
                            challengeName=channel.name,
                            challengerId=challengerObj.id,
                            challengedId=challengedObj.id,
                            actions=[]
                        ).toJSON()
                    dbService.addPendingChallengeScheduledActionGroupToLBUser(
                        challengedObj.id, pendingchallengeGroup
                    )
                    scheduledActionGroup = dbService.getPendingChallengeScheduledActionGroupObjectFromLBUser(
                        challengedObj.id, channel.name)
                actionsToAdd = []
                for action in message_user_jobs:
                    if action.id not in list(map(lambda x: x.id, scheduledActionGroup.actions)):
                        actionsToAdd.append(
                            ScheduledActionModel(
                                actionType="message",
                                actionId=action.id,
                                actionTime=action.next_run_time
                            ).toJSON()
                        )
                if len(actionsToAdd) > 0:
                    for action in actionsToAdd:
                        dbService.addScheduledActionToLBUserPendingChallengeScheduledActionGroup(
                            challengedObj.id, channel.name, action)
            elif reaction.emoji == "❌":
                await reaction.message.delete()
                await channel.send("Challenge Declined!")
                challengerChallenges = dbService.getAllChallengeDataFromLeaderboardUserPendingChallengesById(
                    challengerObj.id)
                challengedChallenges = dbService.getAllChallengeDataFromLeaderboardUserPendingChallengesById(
                    challengedObj.id)
                challengerChallenge = list(filter(
                    lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengerChallenges))[0]
                challengedChallenge = list(filter(
                    lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengedChallenges))[0]
                lbApi.declineChallenge(challengerChallenge)
                # lbApi.declineChallenge(challengedChallenge)
            elif reaction.emoji == "🔴":
                if reaction.count == 3:
                    challengerChallenges = dbService.getAllLeaderboardUserActiveChallengesDataById(
                        challengerObj.id)
                    challengedChallenges = dbService.getAllLeaderboardUserActiveChallengesDataById(
                        challengedObj.id)
                    challengerChallenge = list(filter(
                        lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengerChallenges))[0]
                    challengedChallenge = list(filter(
                        lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengedChallenges))[0]
                    await channel.send("Challenger " + challengerName + " Won!")
                    challengeResultStr = lbApi.onChallengeCompleted(
                        challengerObj, challengedObj, True)
                    # print("Challenge Result String: " + challengeResultStr)
                    await channel.send(challengeResultStr)
                    await channel.send("Deleting channel in 1 minute...")
                    await reaction.message.delete()
                    run_after_1_min(delete_channel, [channel.id])
            elif reaction.emoji == "🔵":
                if reaction.count == 3:
                    challengerChallenges = dbService.getAllLeaderboardUserActiveChallengesDataById(
                        challengerObj.id)
                    challengedChallenges = dbService.getAllLeaderboardUserActiveChallengesDataById(
                        challengedObj.id)
                    challengerChallenge = list(filter(
                        lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengerChallenges))[0]
                    challengedChallenge = list(filter(
                        lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengedChallenges))[0]
                    await channel.send("Challenged " + challengedName + " Won!")
                    challengeResultStr = lbApi.onChallengeCompleted(
                        challengerObj, challengedObj, False)
                    # print("Challenge Result String:" + challengeResultStr)
                    await channel.send(challengeResultStr)
                    await channel.send("Deleting channel in 1 minute...")
                    await reaction.message.delete()
                    run_after_1_min(delete_channel, [channel.id])
        elif user.id != client.user.id and user.id == challengerObj.id:
            if reaction.emoji == "✅":
                await reaction.message.remove_reaction(reaction.emoji, user)
            elif reaction.emoji == "❌":
                await reaction.message.remove_reaction(reaction.emoji, user)
            elif reaction.emoji == "🔴":
                if reaction.count == 3:
                    challengerChallenges = dbService.getAllLeaderboardUserActiveChallengesDataById(
                        challengerObj.id)
                    challengedChallenges = dbService.getAllLeaderboardUserActiveChallengesDataById(
                        challengedObj.id)
                    challengerChallenge = list(filter(
                        lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengerChallenges))[0]
                    challengedChallenge = list(filter(
                        lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengedChallenges))[0]
                    await channel.send("Challenger " + challengerName + " Won!")
                    challengeResultStr = lbApi.onChallengeCompleted(
                        challengerObj, challengedObj, True)
                    # print("Challenge Result String:" + challengeResultStr)
                    await channel.send(challengeResultStr)
                    await channel.send("Deleting channel in 1 minute...")
                    await reaction.message.delete()
                    run_after_1_min(delete_channel, [channel.id])
            elif reaction.emoji == "🔵":
                if reaction.count == 3:
                    challengerChallenges = dbService.getAllLeaderboardUserActiveChallengesDataById(
                        challengerObj.id)
                    challengedChallenges = dbService.getAllLeaderboardUserActiveChallengesDataById(
                        challengedObj.id)
                    challengerChallenge = list(filter(
                        lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengerChallenges))[0]
                    challengedChallenge = list(filter(
                        lambda x: x["challenger"]["id"] == challengerObj.id and x["challenged"]["id"] == challengedObj.id, challengedChallenges))[0]
                    await channel.send("Challenged " + challengedName + " Won!")
                    challengeResultStr = lbApi.onChallengeCompleted(
                        challengerObj, challengedObj, False)
                    # print("Challenge Result String:" + challengeResultStr)
                    await channel.send(challengeResultStr)
                    await channel.send("Deleting channel in 1 minute...")
                    await reaction.message.delete()
                    run_after_1_min(delete_channel, [channel.id])
        elif user.id != client.user.id and user.id != challengedObj.id and user.id != challengerObj.id:
            await reaction.message.remove_reaction(reaction.emoji, user)
    # except IndexError:
    #     await channel.send("No challenge found, challenge completed, or challenge declined.")
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
        channel = await category.create_text_channel(str(challenge.challenger.username).lower() + "🔴-vs-🔵" + str(challenge.challenged.username).lower())
        await channel.set_permissions(ctx.guild.default_role, send_messages=False, add_reactions=False)
        await channel.set_permissions(ctx.user, send_messages=True, add_reactions=True)
        await channel.set_permissions(challenged, send_messages=True, add_reactions=True)
        admins = dbService.getAllLeaderboardModeratorData()
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
        removedStr = dbService.removeChallengeFromLeaderboardUserActiveChallengesById(
            user.id, int(cid))
        await ctx.followup.send(content=removedStr)
    except Exception as e:
        await ctx.followup.send(content="Could not remove challenge.\nReason: " + str(e))


@tree.command(name="get-lb-user-active", description="Get a user's active challenges.", guild=discord.Object(id=config['guildId']))
async def get_lb_user_active(ctx, user: discord.User):
    await ctx.response.defer()
    try:
        activeChallenges = dbService.getAllLeaderboardUserActiveChallengesStringsById(
            user.id)
        if len(activeChallenges) == 0:
            await ctx.followup.send(content="Could not find any active challenges for " + str(user) + ".")
        else:
            await ctx.followup.send(content="Found:\n" + str(activeChallenges))
    except Exception as e:
        await ctx.followup.send(content="Could not find any active challenges for " + str(user) + ".\nReason: " + str(e))


@tree.command(name="get-lb-user-challenge-history", description="Get a user's challenge history.", guild=discord.Object(id=config['guildId']))
async def get_lb_user_challenge_history(ctx, user: discord.User):
    await ctx.response.defer()
    try:
        challengeHistory = dbService.getAllLeaderboardUserChallengeHistoryStringsById(
            user.id)
        await ctx.followup.send(content="Found:\n" + str(challengeHistory))
    except Exception as e:
        await ctx.followup.send(content="Could not find any challenge history for " + str(user) + ".\nReason: " + str(e))


@tree.command(name="rm-lb-user-challenge-history", description="Remove a challenge from a user's challenge history.", guild=discord.Object(id=config['guildId']))
async def rm_lb_user_challenge_history(ctx, user: discord.User, cid: str):
    await ctx.response.defer()
    try:
        removedStr = dbService.removeChallengeFromLeaderboardUserChallengeHistoryById(
            user.id, int(cid))
        await ctx.followup.send(content=removedStr)
    except Exception as e:
        await ctx.followup.send(content="Could not remove challenge.\nReason: " + str(e))


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
    try:
        channel = await ctx.guild.create_text_channel(name)
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await channel.set_permissions(challenger, send_messages=True)
        await channel.set_permissions(challenged, send_messages=True)
        admins = dbService.getAllLeaderboardModeratorData()
        for admin in admins:
            await channel.set_permissions(client.get_user(admin["id"]), send_messages=True)
        await channel.send(content=f"{challenger.mention} has challenged {challenged.mention} to a {leaderboard} match!")
        await ctx.followup.send(content="Channel created: " + channel.mention)
    except Exception as e:
        await ctx.followup.send(content="Could not create channel.\nReason: " + str(e))


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
        user = dbService.getLeaderboardModeratorStringById(user.id)
        await ctx.followup.send(content="Found " + str(user))
    except Exception as e:
        await ctx.followup.send(content="Could not find user.")


@tree.command(name="remove-mod-user", description="Remove Moderator User.", guild=discord.Object(id=config['guildId']))
async def remove_mod_user(ctx, user: discord.User):
    await ctx.response.defer()
    try:
        userString = dbService.removeLeaderboardModeratorById(user.id)
        await ctx.followup.send(content=userString)
    except Exception as e:
        await ctx.followup.send(content="Could not find user.")


@tree.command(name="list-mod-users", description="List Moderator Users.", guild=discord.Object(id=config['guildId']))
async def list_mod_users(ctx):
    await ctx.response.defer()
    usersString = dbService.getAllLeaderboardModeratorStrings()
    if usersString != "":
        await ctx.followup.send(content=str(usersString))
    else:
        await ctx.followup.send(content="Could not find any moderators.")


client = client
qcount = 0
team1 = []
team2 = []
total = []
mention = []
max_players = 2

@tree.command(name='queue', description='Queue for a game', guild=discord.Object(id=config['guildId']))
@app_commands.choices(team=[
    app_commands.Choice(name='Team 1', value='team1'),
    app_commands.Choice(name='Team 2', value='team2')
])
async def queue(ctx, team: str):
    global qcount
    global team1
    global team2
    global total
    global max_players
    await ctx.response.defer()
    if qcount < max_players:
        if team == 'team1' and len(team1) < max_players/2:
            team1.append(ctx.user)
            total.append(ctx.user)
            qcount += 1
            # await ctx.followup.send(f'{ctx.user.mention} has joined Team 1')
        elif team == 'team2' and len(team2) < max_players/2:
            team2.append(ctx.user)
            total.append(ctx.user)
            qcount += 1
            # await ctx.followup.send(f'{ctx.user.mention} has joined Team 2')
        else:
            await ctx.followup.send('Invalid team or team is full')
            return
        if qcount != max_players:
            await ctx.followup.send(f'{ctx.user.mention} has joined {team}')
        else:
            hostOfGame = random.choice(total)
            password = random.randint(1000, 9999)
            await ctx.channel.send(f'{hostOfGame.mention} is the host of the game')
            await ctx.channel.send(f'Team 1: {list(map(lambda x: x.mention, team1))}')
            await ctx.channel.send(f'Team 2: {list(map(lambda x: x.mention, team2))}')
            HostEmbed = discord.Embed(
                title = f'{max_players}Mans',
                description = 'You\'re the host so create the lobby and let the other team know once the lobby is up.\n ' + '**Lobby Name:**  OU' + hostOfGame.name + '\n' + '**Password:** OU' + str(password),
                colour = discord.Colour.green()
            )
            Team1Embed = discord.Embed(
                title = f'{max_players}Mans',
                description = '**Host:** ' + f'{hostOfGame.name}\n' + 'You\'re on the blue team, please keep an eye on the 6mans channel for an update from the host as to when the lobby is up.\n' + '**Lobby Name:** OU ' + hostOfGame.name + '\n' + '**Password:** OU' + str(password),
                colour = discord.Colour.blue()
            )
            Team2Embed = discord.Embed(
                title = f'{max_players}Mans',
                description = '**Host:** ' + f'{hostOfGame.name}\n' + 'You\'re on the orange team, please keep an eye on the 6mans channel for an update from the host as to when the lobby is up.\n' + '**Lobby Name:** OU ' + hostOfGame.name + '\n' + '**Password:** OU' + str(password),
                colour = discord.Colour.orange()
            )
            for p in team1:
                await p.send(embed=Team1Embed)
            for p in team2:
                await p.send(embed=Team2Embed)
            await hostOfGame.send(embed=HostEmbed)
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            team1VC = await ctx.guild.create_voice_channel('Team 1', overwrites=overwrites)
            team2VC = await ctx.guild.create_voice_channel('Team 2', overwrites=overwrites)
            await team1VC.set_permissions(ctx.guild.default_role, connect=False)
            await team2VC.set_permissions(ctx.guild.default_role, connect=False)
            await team1VC.set_permissions(ctx.guild.me, connect=True)
            await team2VC.set_permissions(ctx.guild.me, connect=True)
            for p in team1:
                await team1VC.set_permissions(p, connect=True)
            for p in team2:
                await team2VC.set_permissions(p, connect=True)
            await ctx.channel.send(f'{team1VC.mention} and {team2VC.mention} have been created')
            await ctx.channel.send(f'**Lobby Name:** OU {hostOfGame.name}\n' + f'**Password:** OU {password}')
            qcount = 0
            team1 = []
            team2 = []
            total = []
            mention = []
            await ctx.followup.send('Start the game!')
    else:
        await ctx.followup.send('Queue is full')
    
@tree.command(name='leave', description='Leave the queue', guild=discord.Object(id=config['guildId']))
async def leave(ctx):
    global qcount
    global team1
    global team2
    global total
    global max_players
    await ctx.response.defer()
    if ctx.user in team1:
        team1.remove(ctx.user)
        total.remove(ctx.user)
        qcount -= 1
        await ctx.followup.send(f'{ctx.user.mention} has left the queue')
    elif ctx.user in team2:
        team2.remove(ctx.user)
        total.remove(ctx.user)
        qcount -= 1
        await ctx.followup.send(f'{ctx.user.mention} has left the queue')
    else:
        await ctx.followup.send('You\'re not in the queue')

@tree.command(name='status', description='Check the status of the queue', guild=discord.Object(id=config['guildId']))
async def status(ctx):
    global qcount
    global team1
    global team2
    global total
    global max_players
    await ctx.response.defer()
    StatusEmbed = discord.Embed(
        title = f'{qcount}/{max_players}',
        description = f'Team 1: {list(map(lambda x: x.mention, team1))}\nTeam 2: {list(map(lambda x: x.mention, team2))} \nTotal: {list(map(lambda x: x.mention, total))}',
        colour = discord.Colour.blue()
    )
    await ctx.followup.send(embed=StatusEmbed)

@tree.command(name='remove', description='Remove a player from the queue', guild=discord.Object(id=config['guildId']))
async def remove(ctx, member: discord.Member):
    global qcount
    global team1
    global team2
    global total
    global max_players
    await ctx.response.defer()
    if member in team1:
        team1.remove(member)
        total.remove(member)
        qcount -= 1
        await ctx.followup.send(f'{member.mention} has been removed from the queue')
    elif member in team2:
        team2.remove(member)
        total.remove(member)
        qcount -= 1
        await ctx.followup.send(f'{member.mention} has been removed from the queue')
    else:
        await ctx.followup.send('That player is not in the queue')

@tree.command(name='clear', description='Clear the queue', guild=discord.Object(id=config['guildId']))
async def clear(ctx):
    global qcount
    global team1
    global team2
    global total
    global max_players
    await ctx.response.defer()
    team1 = []
    team2 = []
    total = []
    qcount = 0
    await ctx.followup.send('Queue has been cleared')


# setup(client)

scheduler.start()
t = threading.Thread(target=loop_in_thread, args=(asyncio.get_event_loop(),), daemon=True)
t.start()


client.run(config['token'])
