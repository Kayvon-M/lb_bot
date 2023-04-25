import datetime
import json
from source.core.utils.time_utils import dateTimeToDateStr, getNowAsStr
from source.data.models.base_models import ChallengeModel, LBUserModel

from source.data.models.services.tinydb.tinydb_service import TinyDBService

# Load config
with open('source/config/config.json') as f:
    config = json.load(f)


class LBApi:
    def __init__(self):
        self.maxActiveMandatoryChallenge = config["challengeSettings"]['maxActiveMandatoryChallenges']
        self.defaultChallengeExpirationDays = config["challengeSettings"]['defaultChallengeExpirationDays']
        self.maxChallengeRanksAboveForMandatory = config[
            "challengeSettings"]['maxChallengeRanksAboveForMandatory']
        self.maxChallengeRanksBelowForMandatory = config[
            "challengeSettings"]['maxChallengeRanksBelowForMandatory']
        self.dbService = TinyDBService()

    def getLeaderboardUsersRanked(self, leaderboard):
        users = self.dbService.getLeaderboardUsersDataByLeaderboard(
            leaderboard)
        if leaderboard == "mw2":
            users.sort(key=lambda x: x["mw2Elo"], reverse=True)
        elif leaderboard == "bo2":
            users.sort(key=lambda x: x["bo2Elo"], reverse=True)
        elif leaderboard == "mwii":
            users.sort(key=lambda x: x["mwiiElo"], reverse=True)
        else:
            raise Exception("Invalid leaderboard: " + leaderboard)
        return users

    def addChallengeToPending(self, challengerId, challengedId, leaderboard, challenge):
        users = self.dbService.getLeaderboardUsersDataByLeaderboard(
            leaderboard)
        try:
            challenger = list(
                filter(lambda x: x["id"] == challengerId, users))[0]
            challenged = list(
                filter(lambda x: x["id"] == challengedId, users))[0]
            if challenger["id"] == challenged["id"]:
                raise Exception("Challenger and challenged are the same user.")
            self.dbService.addChallengeToLeaderboardUserPendingChallenges(
                challengerId, challenge)
            self.dbService.addChallengeToLeaderboardUserPendingChallenges(
                challengedId, challenge)
        except IndexError:
            raise Exception("Invalid challenger or challenged ID.")

    def challengeLBUser(self, challengerId, challengedId, leaderboard):
        usersRanked = self.getLeaderboardUsersRanked(leaderboard)
        try:
            challenger = list(
                filter(lambda x: x["id"] == challengerId, usersRanked))[0]
            challengerObj = LBUserModel(
                id=challenger["id"],
                username=challenger["username"],
                isBanned=challenger["isBanned"],
                isModerator=challenger["isModerator"],
                leaderboards=challenger["leaderboards"],
                joinDate=challenger["joinDate"],
                lastActiveDate=getNowAsStr(),
                mw2Elo=challenger["mw2Elo"],
                bo2Elo=challenger["bo2Elo"],
                mwiiElo=challenger["mwiiElo"],
                matchHistory=challenger["matchHistory"],
                activeChallenges=challenger["activeChallenges"],
                pendingChallenges=challenger["pendingChallenges"],
                challengeHistory=challenger["challengeHistory"],
                moderationHistory=challenger["moderationHistory"],
            )
            challenged = list(
                filter(lambda x: x["id"] == challengedId, usersRanked))[0]
            challengedObj = LBUserModel(
                id=challenged["id"],
                username=challenged["username"],
                isBanned=challenged["isBanned"],
                isModerator=challenged["isModerator"],
                leaderboards=challenged["leaderboards"],
                joinDate=challenged["joinDate"],
                lastActiveDate=getNowAsStr(),
                mw2Elo=challenged["mw2Elo"],
                bo2Elo=challenged["bo2Elo"],
                mwiiElo=challenged["mwiiElo"],
                matchHistory=challenged["matchHistory"],
                activeChallenges=challenged["activeChallenges"],
                pendingChallenges=challenged["pendingChallenges"],
                challengeHistory=challenged["challengeHistory"],
                moderationHistory=challenged["moderationHistory"],
            )
            if list(filter(lambda x: x["challenger"]["id"] == challengerId and x["challenged"]["id"] == challengedId, challengerObj.activeChallenges)) != []:
                raise Exception(
                    "Challenger already has an active challenge against this player.")
            if list(filter(lambda x: x["challenger"]["id"] == challengerId and x["challenged"]["id"] == challengedId, challengerObj.pendingChallenges)) != []:
                raise Exception(
                    "Challenger already has a pending challenge against this player.")
            if len(challengerObj.activeChallenges) + len(challengerObj.pendingChallenges) >= self.maxActiveMandatoryChallenge:
                raise Exception(
                    "Challenger already has the maximum number of active challenges.")
            if len(challengedObj.activeChallenges) + len(challengedObj.pendingChallenges) >= self.maxActiveMandatoryChallenge:
                raise Exception(
                    "Challenged Player already has the maximum number of active challenges.")
            challengerIds = list(
                map(lambda x: x["id"], challengerObj.pendingChallenges))
            challengedIds = list(
                map(lambda x: x["id"], challengedObj.pendingChallenges))
            if len(challengerIds) == 0:
                newChallengerChallengeId = 0
            else:
                newChallengerChallengeId = 1 if min(
                    challengerIds) == 0 else 0
            if len(challengedIds) == 0:
                newChallengedChallengeId = 0
            else:
                newChallengedChallengeId = 1 if min(
                    list(map(lambda x: x["id"], challengedObj.pendingChallenges))) == 1 else 0
            if list(usersRanked).index(challenger) - list(usersRanked).index(challenged) > self.maxChallengeRanksAboveForMandatory or list(usersRanked).index(challenger) - list(usersRanked).index(challenged) < -self.maxChallengeRanksBelowForMandatory:
                # add non-mandatory challenge
                challengerChallenge = ChallengeModel(
                    id=newChallengerChallengeId,
                    challengeTime=getNowAsStr(),
                    challenger=challengerObj,
                    challenged=challengedObj,
                    leaderboard=leaderboard,
                    isAccepted=False,
                    isMandatory=False,
                    expiryTime=dateTimeToDateStr(datetime.datetime.now(
                    ) + datetime.timedelta(days=self.defaultChallengeExpirationDays)),
                    result=None
                )
                challengedChallenge = ChallengeModel(
                    id=newChallengedChallengeId,
                    challengeTime=getNowAsStr(),
                    challenger=challengerObj,
                    challenged=challengedObj,
                    leaderboard=leaderboard,
                    isAccepted=False,
                    isMandatory=False,
                    expiryTime=dateTimeToDateStr(datetime.datetime.now(
                    ) + datetime.timedelta(days=self.defaultChallengeExpirationDays)),
                    result=None
                )
                self.dbService.addChallengeToLeaderboardUserPendingChallenges(
                    challengerId, challengerChallenge.toJSON())
                self.dbService.addChallengeToLeaderboardUserPendingChallenges(
                    challengedId, challengedChallenge.toJSON())
                return challengerChallenge
            else:
                # add mandatory challenge
                challengerChallenge = ChallengeModel(
                    id=newChallengerChallengeId,
                    challengeTime=getNowAsStr(),
                    challenger=challengerObj,
                    challenged=challengedObj,
                    leaderboard=leaderboard,
                    isAccepted=False,
                    isMandatory=True,
                    expiryTime=dateTimeToDateStr(datetime.datetime.now(
                    ) + datetime.timedelta(days=self.defaultChallengeExpirationDays)),
                    result=None
                )
                challengedChallenge = ChallengeModel(
                    id=newChallengedChallengeId,
                    challengeTime=getNowAsStr(),
                    challenger=challengerObj,
                    challenged=challengedObj,
                    leaderboard=leaderboard,
                    isAccepted=False,
                    isMandatory=True,
                    expiryTime=dateTimeToDateStr(datetime.datetime.now(
                    ) + datetime.timedelta(days=self.defaultChallengeExpirationDays)),
                    result=None
                )
                self.dbService.addChallengeToLeaderboardUserPendingChallenges(
                    challengerId, challengerChallenge.toJSON())
                self.dbService.addChallengeToLeaderboardUserPendingChallenges(
                    challengedId, challengedChallenge.toJSON())
                return challengerChallenge
        except IndexError:
            raise Exception("Invalid challenger or challenged ID.")
        except Exception as e:
            raise Exception(e)

    def removeChallengeFromLBUserPendingChallenges(self, userId, challengeId):
        try:
            removedChallenge = self.dbService.removeChallengeFromLeaderboardUserPendingChallenges(
                userId, challengeId)
            if removedChallenge.challenger.id == userId:
                self.dbService.removeChallengeFromLeaderboardUserPendingChallenges(
                    removedChallenge.challenged.id, challengeId)
            else:
                self.dbService.removeChallengeFromLeaderboardUserPendingChallenges(
                    removedChallenge.challenger.id, challengeId)
            return "Removed " + str(removedChallenge) + " from " + str(removedChallenge.challenger.username) + "'s pending challenges."
        except IndexError:
            raise Exception("Invalid user ID or challenge ID.")

    def removeAllChallengesFromLBUserPendingChallenges(self, userId):
        try:
            removedChallenges = self.dbService.removeAllChallengesFromLeaderboardUserPendingChallenges(
                userId)
            return removedChallenges
        except IndexError:
            raise Exception("Invalid user ID.")
