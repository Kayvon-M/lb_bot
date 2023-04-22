import datetime


Leaderboards = {
    "mw2": "mw2",
    "bo2": "bo2",
    "mwii": "mwii",
}


class BaseUserModel(object):
    def __init__(self, id, username, isBanned, isModerator, leaderboards, joinDate, lastActiveDate):
        self.id = id
        self.username = username
        self.isBanned = isBanned
        self.isModerator = isModerator
        self.leaderboards = leaderboards
        self.joinDate = joinDate
        self.lastActiveDate = lastActiveDate

    def __str__(self):
        return "User: " + self.username + " with ID " + self.id + " joined on " + self.joinDate + " and last active on " + self.lastActiveDate

    def __repr__(self):
        return "User: " + self.username + " with ID " + self.id + " joined on " + self.joinDate + " and last active on " + self.lastActiveDate

    def isUserBanned(self):
        return self.isBanned

    def isUserModerator(self):
        return self.isModerator


class LBUserModel(BaseUserModel):
    def __init__(self, id, username, isBanned, isModerator, leaderboards, joinDate, lastActiveDate, mw2Elo, bo2Elo, mwiiElo, matchHistory, activeChallenges, pendingChallenges, challengeHistory, moderationHistory):
        super().__init__(id, username, isBanned, isModerator,
                         leaderboards, joinDate, lastActiveDate)
        self.mw2Elo = mw2Elo
        self.bo2Elo = bo2Elo
        self.mwiiElo = mwiiElo
        self.matchHistory = matchHistory
        self.activeChallenges = activeChallenges
        self.pendingChallenges = pendingChallenges
        self.challengeHistory = challengeHistory
        self.moderationHistory = moderationHistory

    def __str__(self):
        return "User: " + self.username + " with ID " + str(self.id) + " joined on " + self.joinDate + " and last active on " + self.lastActiveDate + " and has stats on " + ", ".join(self.leaderboards)

    def __repr__(self):
        return "User: " + self.username + " with ID " + str(self.id) + " joined on " + self.joinDate + " and last active on " + self.lastActiveDate + " and has stats on " + ", ".join(self.leaderboards)

    def getUserStats(self, leaderboard):
        if leaderboard in self.leaderboards:
            return self.lbStats[leaderboard]
        else:
            return None

    def toJSON(self):
        return {
            "id": self.id,
            "username": self.username,
            "isBanned": self.isBanned,
            "isModerator": self.isModerator,
            "leaderboards": self.leaderboards,
            "joinDate": self.joinDate,
            "lastActiveDate": self.lastActiveDate,
            "mw2Elo": self.mw2Elo,
            "bo2Elo": self.bo2Elo,
            "mwiiElo": self.mwiiElo,
            "matchHistory": list(map(lambda x: x.toJSON(), self.matchHistory)),
            "activeChallenges": list(map(lambda x: x.toJSON(), self.activeChallenges)),
            "pendingChallenges": list(map(lambda x: x.toJSON(), self.pendingChallenges)),
            "challengeHistory": list(map(lambda x: x.toJSON(), self.challengeHistory)),
            "moderationHistory": list(map(lambda x: x.toJSON(), self.moderationHistory))
        }

    def fromJSON(self, json):
        self.id = json["id"]
        self.username = json["username"]
        self.isBanned = json["isBanned"]
        self.isModerator = json["isModerator"]
        self.leaderboards = json["leaderboards"]
        self.joinDate = json["joinDate"]
        self.lastActiveDate = json["lastActiveDate"]
        self.mw2Elo = json["mw2Elo"]
        self.bo2Elo = json["bo2Elo"]
        self.mwiiElo = json["mwiiElo"]
        self.matchHistory = list(map(
            lambda x: ChallengeResultModel().fromJSON(x), json["matchHistory"]))
        self.activeChallenges = list(map(
            lambda x: ChallengeModel().fromJSON(x), json["activeChallenges"]))
        self.pendingChallenges = list(map(
            lambda x: ChallengeModel().fromJSON(x), json["pendingChallenges"]))
        self.challengeHistory = list(map(
            lambda x: ChallengeModel().fromJSON(x), json["challengeHistory"]))
        self.moderationHistory = list(map(
            lambda x: ModerationActionModel().fromJSON(x), json["moderationHistory"]))
        return self


ModerationActions = {
    "ban": "ban",
    "unban": "unban",
    "warn": "warn",
    "manageElo": "manageElo",
    "manageLeaderboard": "manageLeaderboard",
    "manageChallenges": "manageChallenges",
    "manageDeclines": "manageDeclines",
    "manageMatchHistory": "manageMatchHistory",
    "mod": "mod",
    "unmod": "unmod",
    "nuke": "nuke",
}


class ModerationActionModel(object):
    def __init__(self, action, moderator, target, reason, actionTime):
        self.action = action
        self.moderator = moderator
        self.target = target
        self.reason = reason
        self.actionTime = actionTime

    def __str__(self):
        return "Moderation action: " + self.moderator + " " + self.action + " " + self.target + " at " + self.actionTime

    def __repr__(self):
        return "Moderation action: " + self.moderator + " " + self.action + " " + self.target + " at " + self.actionTime


class LBModeratorModel(BaseUserModel):
    def __init__(self, id, username, isBanned, isModerator, leaderboards, joinDate, lastActiveDate, moderationHistory):
        super().__init__(id, username, isBanned, isModerator,
                         leaderboards, joinDate, lastActiveDate)
        self.moderationHistory = moderationHistory

    def __str__(self):
        return "Moderator: " + self.username + " with ID " + str(self.id) + " joined on " + self.joinDate + " and last active on " + self.lastActiveDate + " and is mod for " + ", ".join(self.leaderboards)

    def __repr__(self):
        return "Moderator: " + self.username + " with ID " + str(self.id) + " joined on " + self.joinDate + " and last active on " + self.lastActiveDate + " and is mod for " + ", ".join(self.leaderboards)

    def getUserModerationHistory(self):
        return self.moderationHistory

    def toJSON(self):
        return {
            "id": self.id,
            "username": self.username,
            "isBanned": self.isBanned,
            "isModerator": self.isModerator,
            "leaderboards": self.leaderboards,
            "joinDate": self.joinDate,
            "lastActiveDate": self.lastActiveDate,
            "moderationHistory": list(map(lambda x: x.toJSON(), self.moderationHistory)),
        }

    def fromJSON(self, json):
        return LBModeratorModel(json["id"], json["username"], json["isBanned"], json["isModerator"], json["leaderboards"], json["joinDate"], json["lastActiveDate"], json["moderationHistory"])


ChallengePossibleOutcomes = {
    "win": "win",
    "loss": "loss",
    "draw": "draw",
    "dq": "dq",
}


class ChallengeResultModel(object):
    def __init__(self, challenger, challenged, leaderboard, result, resultTime):
        self.challenger = challenger
        self.challenged = challenged
        self.leaderboard = leaderboard
        self.result = result
        self.resultTime = resultTime

    def __str__(self):
        return "Challenge result: " + self.challenger + " challenged " + self.challenged + " on " + self.leaderboard + " and the result was " + self.result + " at " + self.resultTime

    def __repr__(self):
        return "Challenge result: " + self.challenger + " challenged " + self.challenged + " on " + self.leaderboard + " and the result was " + self.result + " at " + self.resultTime

    def toJSON(self):
        return {
            "challenger": LBUserModel(self.challenger).toJSON(),
            "challenged": LBUserModel(self.challenged).toJSON(),
            "leaderboard": self.leaderboard,
            "result": self.result,
            "resultTime": self.resultTime
        }

    def fromJSON(self, json):
        self.challenger = LBUserModel(json["challenger"])
        self.challenged = LBUserModel(json["challenged"])
        self.leaderboard = json["leaderboard"]
        self.result = json["result"]
        self.resultTime = json["resultTime"]


class ChallengeModel(object):
    def __init__(self, challengeTime, challenger, challenged, leaderboard, isAccepted, isMandatory, expiryTime, result):
        self.challengeTime = challengeTime
        self.challenger = challenger
        self.challenged = challenged
        self.leaderboard = leaderboard
        self.isAccepted = isAccepted
        self.isMandatory = isMandatory
        self.expiryTime = expiryTime
        self.result = result

    def __str__(self):
        return "Challenge: " + self.challenger + " challenged " + self.challenged + " on " + self.leaderboard + " at " + self.challengeTime + " and expires at " + self.expiryTime

    def __repr__(self):
        return "Challenge: " + self.challenger + " challenged " + self.challenged + " on " + self.leaderboard + " at " + self.challengeTime + " and expires at " + self.expiryTime

    def isChallengeExpired(self):
        return datetime.datetime.now() > self.expiryTime

    def isChallengePending(self):
        return self.isAccepted == False and self.isChallengeExpired() == False

    def isChallengeRejected(self):
        return self.isAccepted == False and self.isChallengeExpired() == True

    def isChallengeActive(self):
        return self.isAccepted == True and self.isChallengeExpired() == False

    def isChallengeCompleted(self):
        return self.isAccepted == True and self.isChallengeExpired() == True

    def getChallengeStatus(self):
        if self.isChallengeExpired():
            return "Expired"
        if self.isChallengePending():
            return "Pending"
        elif self.isChallengeRejected():
            return "Rejected"
        elif self.isChallengeActive():
            return "Active"
        elif self.isChallengeCompleted():
            return "Completed"
        else:
            return "Unknown"

    def toJSON(self):
        return {
            "challengeTime": self.challengeTime,
            "challenger": LBUserModel(self.challenger).toJSON(),
            "challenged": LBUserModel(self.challenged).toJSON(),
            "leaderboard": self.leaderboard,
            "isAccepted": self.isAccepted,
            "isMandatory": self.isMandatory,
            "expiryTime": self.expiryTime,
            "result": ChallengePossibleOutcomes[self.result].toJSON()
        }

    def fromJSON(self, json):
        self.challengeTime = json["challengeTime"]
        self.challenger = LBUserModel(json["challenger"])
        self.challenged = LBUserModel(json["challenged"])
        self.leaderboard = json["leaderboard"]
        self.isAccepted = json["isAccepted"]
        self.isMandatory = json["isMandatory"]
        self.expiryTime = json["expiryTime"]
        self.result = ChallengePossibleOutcomes[json["result"]]
        return self
