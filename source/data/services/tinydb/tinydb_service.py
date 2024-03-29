import json
import re
import discord
from tinydb import TinyDB, Query
from source.core.utils.time_utils import getNowAsStr

from source.data.models.base_models import ChallengeModel, ChallengeModelFromJSON, ChallengeResultModelFromJSON, LBModeratorModel, LBUserModel, LBUserModelFromJSON


class TinyDBService:
    def __init__(self):
        self.db = TinyDB('db.json')
        self.lbUsersTable = 'users'
        self.lbModeratorTable = 'moderators'
        self.logsTable = 'logs'

    def documentToDict(self, document):
        return json.loads(document)

    def addLeaderboardUser(self, user):
        lbUserUsernames = [str(user['username']).lower() for user in self.db.table(
            self.lbUsersTable).all()]
        if str(user.username).lower() in lbUserUsernames:
            raise Exception("Username must be unique")
        self.db.table(self.lbUsersTable).insert(user.toJSON())

    def getLeaderboardUser(self, userId):
        user = self.db.table(self.lbUsersTable).get(
            Query().id == userId)
        if user is None:
            return None
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

    def getLeaderboardUserDataById(self, userId):
        user = self.db.table(self.lbUsersTable).get(
            Query().id == userId)
        if user is None:
            return None
        return user

    def getLeaderboardUserDataByUsername(self, username):
        user = self.db.table(self.lbUsersTable).get(
            Query().username.matches(username, flags=re.IGNORECASE))
        # Query().username == username)
        if user is None:
            raise Exception("User not found")
        # print(user)
        return user

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

    def updateLeaderboardUserElo(self, userId, leaderboard, elo):
        user = self.db.table(self.lbUsersTable).get(
            Query().id == userId)
        userString = LBUserModelFromJSON(user)
        if leaderboard == 'mw2':
            userString.mw2Elo = elo
        elif leaderboard == 'bo2':
            userString.bo2Elo = elo
        elif leaderboard == 'mwii':
            userString.mwiiElo = elo
        else:
            raise Exception("Invalid leaderboard")
        self.db.table(self.lbUsersTable).update(
            {'mw2Elo': userString.mw2Elo, 'bo2Elo': userString.bo2Elo, 'mwiiElo': userString.mwiiElo}, Query().id == userId)
        return "Updated " + str(userString) + " " + str(leaderboard) + " elo to " + str(elo)

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

    def getLeaderboardUsersData(self):
        return self.db.table(self.lbUsersTable).all()

    def getLeaderboardUsersByLeaderboard(self, leaderboard):
        userStrings = []
        for user in self.db.table(self.lbUsersTable).search(Query().leaderboards.any([leaderboard])):
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
            userStrings.append("\t" + str(lbUserObj))
        return str(leaderboard).upper() + " Users:\n" + ",\n".join(userStrings)

    def getLeaderboardUsersDataByLeaderboard(self, leaderboard):
        return self.db.table(self.lbUsersTable).search(Query().leaderboards.any([leaderboard]))

    def getLeaderboardUserCount(self):
        return len(self.db.table(self.lbUsersTable).all())

    def getLeaderboardUserCountByLeaderboard(self, leaderboard):
        return self.db.table(self.lbUsersTable).count(Query().leaderboards.any([leaderboard]))

    def addChallengeToLeaderboardUserPendingChallenges(self, userId, challenge):
        user = self.db.table(self.lbUsersTable).get(Query().id == userId)
        userMandatoryChallenges = list(
            filter(lambda x: x['isMandatory'] == True, user['pendingChallenges']))
        if len(userMandatoryChallenges) == 0:
            self.db.table(self.lbUsersTable).update(
                {'pendingChallenges': [challenge]}, Query().id == userId)
            self.db.table(self.lbUsersTable).update(
                {'lastActiveDate': getNowAsStr()}, Query().id == userId)
        elif len(userMandatoryChallenges) == 1:
            self.db.table(self.lbUsersTable).update(
                {'pendingChallenges': [user['pendingChallenges'][0], challenge]}, Query().id == userId)
            self.db.table(self.lbUsersTable).update(
                {'lastActiveDate': getNowAsStr()}, Query().id == userId)
        elif len(userMandatoryChallenges) == 2:
            raise Exception("User already has 2 pending mandatory challenges")
        user = self.db.table(self.lbUsersTable).get(Query().id == userId)
        lbUser = LBUserModel(
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
        return "Added " + str(challenge) + " to " + str(lbUser)

    def addChallengeToLeaderboardUserActiveChallenges(self, userId, challenge):
        user = self.db.table(self.lbUsersTable).get(Query().id == userId)
        if (len(user['activeChallenges']) == 0):
            self.db.table(self.lbUsersTable).update(
                {'activeChallenges': [challenge]}, Query().id == userId)
            self.db.table(self.lbUsersTable).update(
                {'lastActiveDate': getNowAsStr()}, Query().id == userId)
        elif (len(user['activeChallenges']) == 1):
            self.db.table(self.lbUsersTable).update(
                {'activeChallenges': [user['activeChallenges'][0], challenge]}, Query().id == userId)
            self.db.table(self.lbUsersTable).update(
                {'lastActiveDate': getNowAsStr()}, Query().id == userId)
        elif (len(user['activeChallenges']) == 2):
            raise Exception("User already has 2 active challenges")
        user = self.db.table(self.lbUsersTable).get(Query().id == userId)
        lbUser = LBUserModel(
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
        return "Added " + str(challenge) + " to " + str(lbUser)

    def getLeaderboardUserActiveChallengesById(self, userId):
        try:
            user = self.db.table(self.lbUsersTable).get(Query().id == userId)
            activeChallengesStr = ""
            if len(user['activeChallenges']) == 0:
                raise Exception("User does not have any active challenges")
            else:
                for challenge in user['activeChallenges']:
                    challengeObj = ChallengeModelFromJSON(challenge)
                    activeChallengesStr += str(challengeObj) + "\n"
            return activeChallengesStr
        except TypeError:
            raise Exception("User does not exist")

    def getLeaderboardUserActiveChallengesDataById(self, userId):
        try:
            user = self.db.table(self.lbUsersTable).get(Query().id == userId)
            if len(user['activeChallenges']) == 0:
                raise Exception("User does not have any active challenges")
            else:
                return user['activeChallenges']
        except TypeError:
            raise Exception("User does not exist")

    def removeChallengeFromLeaderboardUserActiveChallenges(self, userId, challengeId):
        user = self.db.table(self.lbUsersTable).get(Query().id == userId)
        if len(user['activeChallenges']) == 0:
            raise Exception("User does not have any active challenges")
        else:
            challenge = next(
                (x for x in user['activeChallenges'] if x['id'] == challengeId), None)
            if challenge is None:
                raise Exception(
                    "User does not have an active challenge with that id")
            challengeObj = ChallengeModelFromJSON(challenge)
            otherPlayersId = challengeObj.challenger.id if userId == challengeObj.challenged.id else challengeObj.challenged.id
            self.db.table(self.lbUsersTable).update(
                {'activeChallenges': list(filter(lambda x: x['id'] != challengeId, user['activeChallenges']))}, Query().id == userId)
            self.db.table(self.lbUsersTable).update(
                {'lastActiveDate': getNowAsStr()}, Query().id == userId)
            self.db.table(self.lbUsersTable).update(
                {'activeChallenges': list(filter(lambda x: x['id'] != challengeId, user['activeChallenges']))}, Query().id == otherPlayersId)
            self.db.table(self.lbUsersTable).update(
                {'lastActiveDate': getNowAsStr()}, Query().id == otherPlayersId)
            user = self.db.table(self.lbUsersTable).get(Query().id == userId)
            lbUser = LBUserModel(
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
            return "Removed " + str(challengeObj) + " from " + str(lbUser)

    def addChallengeToLeaderboardUserChallengeHistory(self, userId, challengeResult):
        user = self.db.table(self.lbUsersTable).get(Query().id == userId)
        userChallengeHistory = user['challengeHistory']
        # print(challengeResult)
        userChallengeHistory.append(challengeResult)
        self.db.table(self.lbUsersTable).update(
            {'challengeHistory': userChallengeHistory}, Query().id == userId)
        self.db.table(self.lbUsersTable).update(
            {'lastActiveDate': getNowAsStr()}, Query().id == userId)
        user = self.db.table(self.lbUsersTable).get(Query().id == userId)
        lbUser = LBUserModel(
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
        return "Added " + str(challengeResult) + " to " + str(lbUser)
    
    def getLeaderboardUserChallengeHistoryById(self, userId):
        user = self.db.table(self.lbUsersTable).get(Query().id == userId)
        userChallengeHistory = user['challengeHistory']
        challengeHistoryStr = ""
        if len(userChallengeHistory) == 0:
            raise Exception("User does not have any challenge history")
        else:
            for challenge in userChallengeHistory:
                challengeObj = ChallengeResultModelFromJSON(challenge)
                challengeHistoryStr += str(challengeObj) + "\n"
        return challengeHistoryStr

    def removeChallengeFromLeaderbordUserChallengeHistory(self, userId, challengeId):
        user = self.db.table(self.lbUsersTable).get(Query().id == userId)
        userChallengeHistory = user['challengeHistory']
        challenge = next(
            (x for x in userChallengeHistory if x['id'] == challengeId), None)
        if challenge is None:
            raise Exception(
                "User does not have a challenge with that id in their history")
        challengeObj = ChallengeResultModelFromJSON(challenge)
        userChallengeHistory.remove(challenge)
        self.db.table(self.lbUsersTable).update(
            {'challengeHistory': userChallengeHistory}, Query().id == userId)
        self.db.table(self.lbUsersTable).update(
            {'lastActiveDate': getNowAsStr()}, Query().id == userId)
        user = self.db.table(self.lbUsersTable).get(Query().id == userId)
        lbUser = LBUserModel(
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
        return "Removed " + str(challengeObj) + " from " + str(lbUser)

    def getLeaderboardUserPendingChallenges(self, userId):
        user = self.db.table(self.lbUsersTable).get(Query().id == userId)
        try:
            return user['pendingChallenges']
        except discord.app_commands.errors.CommandInvokeError:
            raise Exception("User does not exist in database")
        except TypeError:
            raise Exception("User does not have any pending challenges")

    def removeChallengeFromLeaderboardUserPendingChallenges(self, userId, challengeId):
        user = self.db.table(self.lbUsersTable).get(Query().id == userId)
        if len(user['pendingChallenges']) == 0:
            raise Exception("User does not have any pending challenges")
        else:
            challenge = next(
                (x for x in user['pendingChallenges'] if x['id'] == challengeId), None)
            if challenge is None:
                raise Exception(
                    "User does not have a pending challenge with that id")
            challengeObj = ChallengeModelFromJSON(challenge)
            self.db.table(self.lbUsersTable).update(
                {'pendingChallenges': list(filter(lambda x: x['id'] != challengeId, user['pendingChallenges']))}, Query().id == userId)
            self.db.table(self.lbUsersTable).update(
                {'lastActiveDate': getNowAsStr()}, Query().id == userId)
            return challengeObj

    def removeAllChallengesFromLeaderboardUserPendingChallenges(self, userId):
        user = self.db.table(self.lbUsersTable).get(Query().id == userId)
        if len(user['pendingChallenges']) == 0:
            raise Exception("User does not have any pending challenges")
        else:
            for challenge in user['pendingChallenges']:
                challengeObj = ChallengeModelFromJSON(challenge)
                self.db.table(self.lbUsersTable).update(
                    {'pendingChallenges': list(filter(lambda x: x['challenger']['id'] != challengeObj.challenger.id and x['challenged']['id'] != challengeObj.challenged.id, user['pendingChallenges']))}, Query().id == challengeObj.challenger.id)
                self.db.table(self.lbUsersTable).update(
                    {'lastActiveDate': getNowAsStr()}, Query().id == challengeObj.challenger.id)
                self.db.table(self.lbUsersTable).update(
                    {'pendingChallenges': list(filter(lambda x: x['challenger']['id'] != challengeObj.challenger.id and x['challenged']['id'] != challengeObj.challenged.id, user['pendingChallenges']))}, Query().id == challengeObj.challenged.id)
                self.db.table(self.lbUsersTable).update(
                    {'lastActiveDate': getNowAsStr()}, Query().id == challengeObj.challenged.id)
            return "Removed all pending challenges from " + str(user['username'])

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
        try:
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
        except:
            pass
        return ",\n".join(userStrings)

    def getLeaderboardModeratorsData(self):
        return self.db.table(self.lbModeratorTable).all()

    def getLogs(self):
        return self.db.table(self.logsTable)
