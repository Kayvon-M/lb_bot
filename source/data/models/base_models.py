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
            "matchHistory": self.matchHistory,
            "activeChallenges": self.activeChallenges,
            "pendingChallenges": self.pendingChallenges,
            "challengeHistory": self.challengeHistory,
            "moderationHistory": self.moderationHistory,
        }


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


class ChallengeModel(object):
    def __init__(self, id, challengeTime, challenger, challenged, leaderboard, isAccepted, isMandatory, expiryTime, result):
        self.id = id
        self.challengeTime = challengeTime
        self.challenger = challenger
        self.challenged = challenged
        self.leaderboard = leaderboard
        self.isAccepted = isAccepted
        self.isMandatory = isMandatory
        self.expiryTime = expiryTime
        self.result = result

    def __str__(self):
        if self.isMandatory:
            return f"Mandatory challenge with id {str(self.id)}: " + str(self.challenger) + " challenged " + str(self.challenged) + " on " + self.leaderboard + " at " + self.challengeTime + " and expires at " + self.expiryTime
        return f"Challenge with id {str(self.id)}: " + str(self.challenger) + " challenged " + str(self.challenged) + " on " + self.leaderboard + " at " + self.challengeTime + " and expires at " + self.expiryTime

    def __repr__(self):
        if self.isMandatory:
            return f"Mandatory challenge with id {str(self.id)}: " + str(self.challenger) + " challenged " + str(self.challenged) + " on " + self.leaderboard + " at " + self.challengeTime + " and expires at " + self.expiryTime
        return f"Challenge with id {str(self.id)}: " + str(self.challenger) + " challenged " + str(self.challenged) + " on " + self.leaderboard + " at " + self.challengeTime + " and expires at " + self.expiryTime

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
            "id": self.id,
            "challengeTime": self.challengeTime,
            "challenger": self.challenger.toJSON(),
            "challenged": self.challenged.toJSON(),
            "leaderboard": self.leaderboard,
            "isAccepted": self.isAccepted,
            "isMandatory": self.isMandatory,
            "expiryTime": self.expiryTime,
            "result": None if self.result is None else self.result.toJSON()
        }


def ModerationActionModelFromJSON(json):
    return ModerationActionModel(
        json["action"],
        json["moderator"],
        json["target"],
        json["reason"],
        json["actionTime"]
    )


def ChallengeResultModelFromJSON(self, json):
    return ChallengeResultModel(
        json["challenger"],
        json["challenged"],
        json["leaderboard"],
        json["result"],
        json["resultTime"]
    )


def LBUserModelFromJSON(json):
    return LBUserModel(
        json["id"],
        json["username"],
        json["isBanned"],
        json["isModerator"],
        json["leaderboards"],
        json["joinDate"],
        json["lastActiveDate"],
        json["mw2Elo"],
        json["bo2Elo"],
        json["mwiiElo"],
        list(map(
            lambda x: ChallengeResultModelFromJSON(x), json["matchHistory"])),
        list(map(
            lambda x: ChallengeModelFromJSON(x), json["activeChallenges"])),
        list(map(
            lambda x: ChallengeModelFromJSON(x), json["pendingChallenges"])),
        list(map(
            lambda x: ChallengeModelFromJSON(x), json["challengeHistory"])),
        list(map(
            lambda x: ModerationActionModelFromJSON(x), json["moderationHistory"]))
    )


def ChallengeModelFromJSON(json):
    return ChallengeModel(
        json["id"],
        json["challengeTime"],
        LBUserModelFromJSON(json["challenger"]),
        LBUserModelFromJSON(json["challenged"]),
        json["leaderboard"],
        json["isAccepted"],
        json["isMandatory"],
        json["expiryTime"],
        json["result"],
    )
