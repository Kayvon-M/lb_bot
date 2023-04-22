import json
from tinydb import TinyDB, Query

from source.data.models.base_models import LBModeratorModel, LBUserModel


class TinyDBService:
    def __init__(self):
        self.db = TinyDB('db.json')
        self.lbUsersTable = 'users'
        self.lbModeratorTable = 'moderators'
        self.logsTable = 'logs'

    def documentToDict(self, document):
        return json.loads(document)

    def addLeaderboardUser(self, user):
        self.db.table(self.lbUsersTable).insert(user.toJSON())

    def getLeaderboardUser(self, userId):
        user = self.db.table(self.lbUsersTable).get(
            Query().id == userId)
        userString = LBUserModel(
            id=user['id'],
            username=user['username'],
            isBanned=user['isBanned'],
            isModerator=user['isModerator'],
            leaderboards=user['leaderboards'],
            joinDate=user['joinDate'],
            lastActiveDate=user['lastActiveDate'],
            mw2Elo=user['mw2Elo'],
            bo2Elo=user['bo2Elo'],
            mwiiElo=user['mwiiElo'],
            matchHistory=user['matchHistory'],
            activeChallenges=user['activeChallenges'],
            pendingChallenges=user['pendingChallenges'],
            challengeHistory=user['challengeHistory'],
            moderationHistory=user['moderationHistory'],
        )
        return "Found " + str(userString)

    def removeLeaderboardUser(self, userId):
        user = self.db.table(self.lbUsersTable).get(
            Query().id == userId)
        userString = LBUserModel(
            id=user['id'],
            username=user['username'],
            isBanned=user['isBanned'],
            isModerator=user['isModerator'],
            leaderboards=user['leaderboards'],
            joinDate=user['joinDate'],
            lastActiveDate=user['lastActiveDate'],
            mw2Elo=user['mw2Elo'],
            bo2Elo=user['bo2Elo'],
            mwiiElo=user['mwiiElo'],
            matchHistory=user['matchHistory'],
            activeChallenges=user['activeChallenges'],
            pendingChallenges=user['pendingChallenges'],
            challengeHistory=user['challengeHistory'],
            moderationHistory=user['moderationHistory'],
        )
        self.db.table(self.lbUsersTable).remove(Query().id == userId)
        return "Removed " + str(userString)

    def getLeaderboardUsers(self):
        userStrings = []
        for user in self.db.table(self.lbUsersTable).all():
            lbUserObj = LBUserModel(
                id=user['id'],
                username=user['username'],
                isBanned=user['isBanned'],
                isModerator=user['isModerator'],
                leaderboards=user['leaderboards'],
                joinDate=user['joinDate'],
                lastActiveDate=user['lastActiveDate'],
                mw2Elo=user['mw2Elo'],
                bo2Elo=user['bo2Elo'],
                mwiiElo=user['mwiiElo'],
                matchHistory=user['matchHistory'],
                activeChallenges=user['activeChallenges'],
                pendingChallenges=user['pendingChallenges'],
                challengeHistory=user['challengeHistory'],
                moderationHistory=user['moderationHistory'],
            )
            userStrings.append(str(lbUserObj))
        return ",\n".join(userStrings)

    def addLeaderboardModerator(self, user):
        self.db.table(self.lbModeratorTable).insert(user.toJSON())

    def getLeaderboardModerator(self, userId):
        user = self.db.table(self.lbModeratorTable).get(
            Query().id == userId)
        userString = LBModeratorModel(
            id=user['id'],
            username=user['username'],
            isBanned=user['isBanned'],
            isModerator=user['isModerator'],
            leaderboards=user['leaderboards'],
            joinDate=user['joinDate'],
            lastActiveDate=user['lastActiveDate'],
            moderationHistory=user['moderationHistory'],
        )
        return "Found " + str(userString)

    def removeLeaderboardModerator(self, userId):
        user = self.db.table(self.lbModeratorTable).get(
            Query().id == userId)
        userString = LBModeratorModel(
            id=user['id'],
            username=user['username'],
            isBanned=user['isBanned'],
            isModerator=user['isModerator'],
            leaderboards=user['leaderboards'],
            joinDate=user['joinDate'],
            lastActiveDate=user['lastActiveDate'],
            moderationHistory=user['moderationHistory'],
        )
        self.db.table(self.lbModeratorTable).remove(Query().id == userId)
        return "Removed " + str(userString)

    def getLeaderboardModerators(self):
        userStrings = []
        # try:
        for user in self.db.table(self.lbModeratorTable).all():
            lbUserObj = LBModeratorModel(
                id=user['id'],
                username=user['username'],
                isBanned=user['isBanned'],
                isModerator=user['isModerator'],
                leaderboards=user['leaderboards'],
                joinDate=user['joinDate'],
                lastActiveDate=user['lastActiveDate'],
                moderationHistory=user['moderationHistory'],
            )
            userStrings.append(str(lbUserObj))
        # except:
        #     pass
        return ",\n".join(userStrings)

    def getLogs(self):
        return self.db.table(self.logsTable)
