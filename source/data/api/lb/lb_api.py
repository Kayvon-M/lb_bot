import datetime
import json
from source.core.utils.elo_utils import getNewRatings
from source.core.utils.time_utils import dateTimeToDateStr, getNowAsStr
from source.data.models.base_models import ChallengeModel, ChallengeModelFromJSON, ChallengeResultModel, LBUserModel, LBUserModelFromJSON

from source.data.services.tinydb.tinydb_service import TinyDBService

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
                user = self.dbService.getLeaderboardUserDataById(
                    removedChallenge.challenged.id)
                challengeToRemove = list(filter(lambda x: x["challenger"]["id"] == removedChallenge.challenger.id and x[
                    "challenged"]["id"] == removedChallenge.challenged.id, user["pendingChallenges"]))[0]
                self.dbService.removeChallengeFromLeaderboardUserPendingChallenges(
                    removedChallenge.challenged.id, challengeToRemove["id"])
            else:
                user = self.dbService.getLeaderboardUserDataById(
                    removedChallenge.challenger.id)
                challengeToRemove = list(filter(lambda x: x["challenger"]["id"] == removedChallenge.challenger.id and x[
                    "challenged"]["id"] == removedChallenge.challenged.id, user["pendingChallenges"]))[0]
                self.dbService.removeChallengeFromLeaderboardUserPendingChallenges(
                    removedChallenge.challenger.id, challengeToRemove["id"])
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

    def acceptChallenge(self, challenge):
        # challenge = ChallengeModelFromJSON(challenge)
        challenger = challenge["challenger"]
        challenged = challenge["challenged"]
        challengerData = self.dbService.getLeaderboardUserDataById(
            challenger["id"])
        # print(challengerData["pendingChallenges"])
        challengedData = self.dbService.getLeaderboardUserDataById(
            challenged["id"])
        # print(challengedData["pendingChallenges"])
        # challengerObj = LBUserModelFromJSON(
        #     challengerData)
        # challengedObj = LBUserModelFromJSON(
        #     challengedData)
        challengerPendingChallenge = list(filter(
            lambda x: x["challenged"]["id"] == challenged["id"], challengerData["pendingChallenges"]))
        challengedPendingChallenge = list(filter(
            lambda x: x["challenger"]["id"] == challenger["id"], challengedData["pendingChallenges"]))
        if len(challengerPendingChallenge) == 0 or len(challengedPendingChallenge) == 0:
            raise Exception("No pending challenge found.")
        # print(challengerPendingChallenge)
        # print(challengedPendingChallenge)
        removedChallengerChallenge = self.dbService.removeChallengeFromLeaderboardUserPendingChallenges(
            challenger["id"], challengerPendingChallenge[0]["id"])
        removedChallengedChallenge = self.dbService.removeChallengeFromLeaderboardUserPendingChallenges(
            challenged["id"], challengedPendingChallenge[0]["id"])
        challengerPendingChallenge[0]["isAccepted"] = True
        challengedPendingChallenge[0]["isAccepted"] = True
        # print(challengerPendingChallenge[0])
        # print(challengedPendingChallenge[0])
        addedActiveChallengerChallenge = self.dbService.addChallengeToLeaderboardUserActiveChallenges(
            challenger["id"], challengerPendingChallenge[0])
        addedActiveChallengedChallenge = self.dbService.addChallengeToLeaderboardUserActiveChallenges(
            challenged["id"], challengedPendingChallenge[0])
        return "Accepted challenge " + str(removedChallengerChallenge) + " from " + str(removedChallengerChallenge.challenger.username) + " to " + str(removedChallengerChallenge.challenged.username) + "."

    def declineChallenge(self, challenge):
        challenge = ChallengeModelFromJSON(challenge)
        challenger = challenge.challenger
        challenged = challenge.challenged
        challengerData = self.dbService.getLeaderboardUserDataById(
            challenger.id)
        challengedData = self.dbService.getLeaderboardUserDataById(
            challenged.id)
        challengerObj = LBUserModelFromJSON(
            challengerData)
        challengedObj = LBUserModelFromJSON(
            challengedData)
        challengerPendingChallenge = list(filter(
            lambda x: x["challenged"]["id"] == challenged.id, challengerData["pendingChallenges"]))[0]
        challengedPendingChallenge = list(filter(
            lambda x: x["challenger"]["id"] == challenger.id, challengedData["pendingChallenges"]))[0]
        removedChallengerChallenge = self.dbService.removeChallengeFromLeaderboardUserPendingChallenges(
            challenger.id, challengerPendingChallenge["id"])
        removedChallengedChallenge = self.dbService.removeChallengeFromLeaderboardUserPendingChallenges(
            challenged.id, challengedPendingChallenge["id"])
        return "Declined challenge " + str(removedChallengerChallenge) + " from " + str(removedChallengerChallenge.challenger.username) + " to " + str(removedChallengerChallenge.challenged.username) + "."

    def onChallengeCompleted(self, challenger, challenged, challengerWon):
        challengerData = self.dbService.getLeaderboardUserDataById(
            challenger.id)
        challengedData = self.dbService.getLeaderboardUserDataById(
            challenged.id)
        challengerObj = LBUserModelFromJSON(
            challengerData)
        challengedObj = LBUserModelFromJSON(
            challengedData)
        challengerActiveChallenge = list(filter(
            lambda x: x["challenged"]["id"] == challenged.id, challengerData["activeChallenges"]))[0]
        challengedActiveChallenge = list(filter(
            lambda x: x["challenger"]["id"] == challenger.id, challengedData["activeChallenges"]))[0]
        if challengerWon:
            challengerResult = ChallengeResultModel(
                challenger=challenger, challenged=challenged, leaderboard=challengerActiveChallenge["leaderboard"], result="win", resultTime=getNowAsStr())
            challengedResult = ChallengeResultModel(
                challenger=challenger, challenged=challenged, leaderboard=challengerActiveChallenge["leaderboard"], result="loss", resultTime=getNowAsStr())
            # print(challengerResult.toJSON())
            self.dbService.addChallengeToLeaderboardUserChallengeHistory(
                challenger.id, challengerResult.toJSON())
            self.dbService.addChallengeToLeaderboardUserChallengeHistory(
                challenged.id, challengedResult.toJSON())
            if challengerActiveChallenge["leaderboard"] == "mw2":
                challengerNewElo = getNewRatings(
                    challenger.mw2Elo, challenged.mw2Elo, "win")[0]
                challengedNewElo = getNewRatings(
                    challenged.mw2Elo, challenger.mw2Elo, "loss")[0]
                self.dbService.updateLeaderboardUserElo(
                    challenger.id, "mw2", challengerNewElo)
                self.dbService.updateLeaderboardUserElo(
                    challenged.id, "mw2", challengedNewElo)
                removedChallengerChallenge = self.dbService.removeChallengeFromLeaderboardUserActiveChallenges(
                    challenger.id, challengerActiveChallenge["id"])
                return "Completed challenge. " + str(challengerObj.username) + " " + str(challengerResult.result) + " " + str(challengedObj.username) + " in " + str(challengerActiveChallenge["leaderboard"]) + ". New Elo: " + str(challengerNewElo) + " " + str(challengedNewElo)
            elif challengerActiveChallenge["leaderboard"] == "bo2":
                challengerNewElo = getNewRatings(
                    challenger.bo2Elo, challenged.bo2Elo, "win")[0]
                challengedNewElo = getNewRatings(
                    challenged.bo2Elo, challenger.bo2Elo, "loss")[0]
                self.dbService.updateLeaderboardUserElo(
                    challenger.id, "bo2", challengerNewElo)
                self.dbService.updateLeaderboardUserElo(
                    challenged.id, "bo2", challengedNewElo)
                removedChallengerChallenge = self.dbService.removeChallengeFromLeaderboardUserActiveChallenges(
                    challenger.id, challengerActiveChallenge["id"])
                return "Completed challenge. " + str(challengerObj.username) + " " + str(challengerResult.result) + " " + str(challengedObj.username) + " in " + str(challengerActiveChallenge["leaderboard"]) + ". New Elo: " + str(challengerNewElo) + " " + str(challengedNewElo)
            elif challengerActiveChallenge["leaderboard"] == "mwii":
                challengerNewElo = getNewRatings(
                    challenger.mwiiElo, challenged.mwiiElo, "win")[0]
                challengedNewElo = getNewRatings(
                    challenged.mwiiElo, challenger.mwiiElo, "loss")[0]
                self.dbService.updateLeaderboardUserElo(
                    challenger.id, "mwii", challengerNewElo)
                self.dbService.updateLeaderboardUserElo(
                    challenged.id, "mwii", challengedNewElo)
                removedChallengerChallenge = self.dbService.removeChallengeFromLeaderboardUserActiveChallenges(
                    challenger.id, challengerActiveChallenge["id"])
                return "Completed challenge. " + str(challengerObj.username) + " " + str(challengerResult.result) + " " + str(challengedObj.username) + " in " + str(challengerActiveChallenge["leaderboard"]) + ". New Elo: " + str(challengerNewElo) + " " + str(challengedNewElo)
        else:
            challengerResult = ChallengeResultModel(
                challenger=challenger, challenged=challenged, leaderboard=challengerActiveChallenge["leaderboard"], result="loss", resultTime=getNowAsStr())
            challengedResult = ChallengeResultModel(
                challenger=challenger, challenged=challenged, leaderboard=challengerActiveChallenge["leaderboard"], result="win", resultTime=getNowAsStr())
            self.dbService.addChallengeToLeaderboardUserChallengeHistory(
                challenger.id, challengerResult.toJSON())
            self.dbService.addChallengeToLeaderboardUserChallengeHistory(
                challenged.id, challengedResult.toJSON())
            if challengerActiveChallenge["leaderboard"] == "mw2":
                challengerNewElo = getNewRatings(
                    challenger.mw2Elo, challenged.mw2Elo, "loss")[0]
                challengedNewElo = getNewRatings(
                    challenged.mw2Elo, challenger.mw2Elo, "win")[0]
                self.dbService.updateLeaderboardUserElo(
                    challenger.id, "mw2", challengerNewElo)
                self.dbService.updateLeaderboardUserElo(
                    challenged.id, "mw2", challengedNewElo)
                removedChallengerChallenge = self.dbService.removeChallengeFromLeaderboardUserActiveChallenges(
                    challenger.id, challengerActiveChallenge["id"])
                return "Completed challenge. " + str(challengerObj.username) + " " + str(challengerResult.result) + " " + str(challengedObj.username) + " in " + str(challengerActiveChallenge["leaderboard"]) + ". New Elo: " + str(challengerNewElo) + " " + str(challengedNewElo)
            elif challengerActiveChallenge["leaderboard"] == "bo2":
                challengerNewElo = getNewRatings(
                    challenger.bo2Elo, challenged.bo2Elo, "loss")[0]
                challengedNewElo = getNewRatings(
                    challenged.bo2Elo, challenger.bo2Elo, "win")[0]
                self.dbService.updateLeaderboardUserElo(
                    challenger.id, "bo2", challengerNewElo)
                self.dbService.updateLeaderboardUserElo(
                    challenged.id, "bo2", challengedNewElo)
                removedChallengerChallenge = self.dbService.removeChallengeFromLeaderboardUserActiveChallenges(
                    challenger.id, challengerActiveChallenge["id"])
                return "Completed challenge. " + str(challengerObj.username) + " " + str(challengerResult.result) + " " + str(challengedObj.username) + " in " + str(challengerActiveChallenge["leaderboard"]) + ". New Elo: " + str(challengerNewElo) + " " + str(challengedNewElo)
            elif challengerActiveChallenge["leaderboard"] == "mwii":
                challengerNewElo = getNewRatings(
                    challenger.mwiiElo, challenged.mwiiElo, "loss")[0]
                challengedNewElo = getNewRatings(
                    challenged.mwiiElo, challenger.mwiiElo, "win")[0]
                self.dbService.updateLeaderboardUserElo(
                    challenger.id, "mwii", challengerNewElo)
                self.dbService.updateLeaderboardUserElo(
                    challenged.id, "mwii", challengedNewElo)
                removedChallengerChallenge = self.dbService.removeChallengeFromLeaderboardUserActiveChallenges(
                    challenger.id, challengerActiveChallenge["id"])
                return "Completed challenge. " + str(challengerObj.username) + " " + str(challengerResult.result) + " " + str(challengedObj.username) + " in " + str(challengerActiveChallenge["leaderboard"]) + ". New Elo: " + str(challengerNewElo) + " " + str(challengedNewElo)
