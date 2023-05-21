import re
from pymongo import MongoClient
from bson import BSON

from source.data.models.base_models import ChallengeModelFromJSON, ChallengeResultModelFromJSON, LBModeratorModelFromJSON, LBUserModelFromJSON


class MongoDBService:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['1v1lb']
        self.lbUsersTable = self.db['lbUsers']
        self.lbModeratorsTable = self.db['lbModerators']
        self.lbQueueTable = self.db['lbQueue']
        self.lbSchedulerTable = self.db['lbScheduler']
        self.logsTable = self.db['logs']

    def addLeaderboardUser(self, user) -> str:
        # user = BSON.encode(user)
        lbUserNames = [str(x['username']).lower() for x in self.lbUsersTable.find()]
        lbUserIds = [x['id'] for x in self.lbUsersTable.find()]
        if str(user["username"]).lower() not in lbUserNames and user["id"] not in lbUserIds:
            self.lbUsersTable.insert_one(user)
            return 'User added to leaderboard'
        else:
            raise Exception('User already exists in leaderboard')
            
    def removeLeaderboardUserById(self, userId) -> str:
        deleteResult = self.lbUsersTable.delete_one({'id': userId})
        if deleteResult.deleted_count == 1:
            return 'User removed from leaderboard'
        else:
            raise Exception('User does not exist in leaderboard')
        
    def removeLeaderboardUserByName(self, userName) -> str:
        deleteResult = self.lbUsersTable.delete_one({'username': re.compile(userName, re.IGNORECASE)})
        if deleteResult.deleted_count == 1:
            return 'User removed from leaderboard'
        else:
            raise Exception('User does not exist in leaderboard')
        
    def getLeaderboardUserStringById(self, userId):
        userData = self.lbUsersTable.find_one({'id': userId})
        if userData:
            userObject = LBUserModelFromJSON(userData)
            return str(userObject)
        else:
            raise Exception('User does not exist in leaderboard')
        
    def getLeaderboardUserStringByName(self, userName):
        userData = self.lbUsersTable.find_one({'username': re.compile(userName, re.IGNORECASE)})
        if userData:
            userObject = LBUserModelFromJSON(userData)
            return str(userObject)
        else:
            raise Exception('User does not exist in leaderboard')
        
    def getLeaderboardUserObjectById(self, userId):
        userData = self.lbUsersTable.find_one({'id': userId})
        if userData:
            userObject = LBUserModelFromJSON(userData)
            return userObject
        else:
            raise Exception('User does not exist in leaderboard')
        
    def getLeaderboardUserObjectByName(self, userName):
        userData = self.lbUsersTable.find_one({'username': re.compile(userName, re.IGNORECASE)})
        if userData:
            userObject = LBUserModelFromJSON(userData)
            return userObject
        else:
            raise Exception('User does not exist in leaderboard')
        
    def getLeaderboardUserDataById(self, userId):
        userData = self.lbUsersTable.find_one({'id': userId})
        if userData:
            return userData
        else:
            raise Exception('User does not exist in leaderboard')
        
    def getLeaderboardUserDataByName(self, userName):
        userData = self.lbUsersTable.find_one({'username': re.compile(userName, re.IGNORECASE)})
        if userData:
            return userData
        else:
            raise Exception('User does not exist in leaderboard')

    def updateLeaderboardUserEloById(self, userId, leaderboard, elo) -> str:
        updateResult = None
        if leaderboard == 'mw2':
            updateResult = self.lbUsersTable.update_one({'id': userId}, {'$set': {'mw2Elo': elo}})
        elif leaderboard == 'bo2':
            updateResult = self.lbUsersTable.update_one({'id': userId}, {'$set': {'bo2Elo': elo}})
        elif leaderboard == 'mwii':
            updateResult = self.lbUsersTable.update_one({'id': userId}, {'$set': {'mwiiElo': elo}})
        else:
            raise Exception('Invalid leaderboard')
        if updateResult.modified_count == 1:
            return 'User elo updated'
        else:
            raise Exception('User does not exist in leaderboard')
        
    def updateLeaderboardUserEloByName(self, userName, leaderboard, elo) -> str:
        updateResult = None
        if leaderboard == 'mw2':
            updateResult = self.lbUsersTable.update_one({'username': re.compile(userName, re.IGNORECASE)}, {'$set': {'mw2Elo': elo}})
        elif leaderboard == 'bo2':
            updateResult = self.lbUsersTable.update_one({'username': re.compile(userName, re.IGNORECASE)}, {'$set': {'bo2Elo': elo}})
        elif leaderboard == 'mwii':
            updateResult = self.lbUsersTable.update_one({'username': re.compile(userName, re.IGNORECASE)}, {'$set': {'mwiiElo': elo}})
        else:
            raise Exception('Invalid leaderboard')
        if updateResult.modified_count == 1:
            return 'User elo updated'
        else:
            raise Exception('User does not exist in leaderboard')
        
    def getAllLeaderboardUsersStrings(self) -> str:
        lbUsers = self.lbUsersTable.find()
        lbUsersCount = self.lbUsersTable.count_documents({})
        lbUsersStrings = []
        # if lbUsersCount == 0:
        #     raise Exception('No users in leaderboard')
        for user in lbUsers:
            userObject = LBUserModelFromJSON(user)
            lbUsersStrings.append(str(userObject))
        return "\n".join(lbUsersStrings)
    
    def getAllLeaderboardUsersObjects(self) -> list:
        lbUsers = self.lbUsersTable.find()
        lbUsersCount = self.lbUsersTable.count_documents({})
        lbUsersData = []
        # if lbUsersCount == 0:
        #     raise Exception('No users in leaderboard')
        for user in lbUsers:
            userObject = LBUserModelFromJSON(user)
            lbUsersData.append(userObject)
        return lbUsersData
    
    def getAllLeaderboardUsersData(self) -> list:
        lbUsers = self.lbUsersTable.find()
        lbUsersCount = self.lbUsersTable.count_documents({})
        lbUsersData = []
        # if lbUsersCount == 0:
        #     raise Exception('No users in leaderboard')
        for user in lbUsers:
            lbUsersData.append(user)
        return lbUsersData
    
    def getLeaderboadUsersStringsByLeaderboard(self, leaderboard) -> str:
        users = None
        usersCount = None
        if leaderboard == "mw2":
            users = self.lbUsersTable.find({'leaderboards': "mw2"}).sort('mw2Elo', -1)
            usersCount = self.lbUsersTable.count_documents({'leaderboards': "mw2"})
        elif leaderboard == "bo2":
            users = self.lbUsersTable.find({'leaderboards': "bo2"}).sort('bo2Elo', -1)
            usersCount = self.lbUsersTable.count_documents({'leaderboards': "bo2"})
        elif leaderboard == "mwii":
            users = self.lbUsersTable.find({'leaderboards': "mwii"}).sort('mwiiElo', -1)
            usersCount = self.lbUsersTable.count_documents({'leaderboards': "mwii"})
        # if usersCount == 0:
        #     raise Exception('No users in leaderboard')
        usersStrings = []
        for user in users:
            userObject = LBUserModelFromJSON(user)
            usersStrings.append(str(userObject))
        return "\n".join(usersStrings)
        
    def getLeaderboadUsersObjectsByLeaderboard(self, leaderboard) -> list:
        users = None
        usersCount = None
        if leaderboard == "mw2":
            users = self.lbUsersTable.find({'leaderboards': "mw2"}).sort('mw2Elo', -1)
            usersCount = self.lbUsersTable.count_documents({'leaderboards': "mw2"})
        elif leaderboard == "bo2":
            users = self.lbUsersTable.find({'leaderboards': "bo2"}).sort('bo2Elo', -1)
            usersCount = self.lbUsersTable.count_documents({'leaderboards': "bo2"})
        elif leaderboard == "mwii":
            users = self.lbUsersTable.find({'leaderboards': "mwii"}).sort('mwiiElo', -1)
            usersCount = self.lbUsersTable.count_documents({'leaderboards': "mwii"})
        # if usersCount == 0:
        #     raise Exception('No users in leaderboard')
        usersData = []
        for user in users:
            userObject = LBUserModelFromJSON(user)
            usersData.append(userObject)
        return usersData
    
    def getLeaderboadUsersDataByLeaderboard(self, leaderboard) -> list:
        users = None
        usersCount = None
        if leaderboard == "mw2":
            users = self.lbUsersTable.find({'leaderboards': "mw2"}).sort('mw2Elo', -1)
            usersCount = self.lbUsersTable.count_documents({'leaderboards': "mw2"})
        elif leaderboard == "bo2":
            users = self.lbUsersTable.find({'leaderboards': "bo2"}).sort('bo2Elo', -1)
            usersCount = self.lbUsersTable.count_documents({'leaderboards': "bo2"})
        elif leaderboard == "mwii":
            users = self.lbUsersTable.find({'leaderboards': "mwii"}).sort('mwiiElo', -1)
            usersCount = self.lbUsersTable.count_documents({'leaderboards': "mwii"})
        # if usersCount == 0:
        #     raise Exception('No users in leaderboard')
        usersData = []
        for user in users:
            usersData.append(user)
        return usersData

    def getAllLeaderboardUsersCount(self) -> int:
        return self.lbUsersTable.count_documents({})
    
    def getLeaderboardUsersCountByLeaderboard(self, leaderboard) -> int:
        return self.lbUsersTable.count_documents({'leaderboards': leaderboard})
    
    def addChallengeToLeaderboardUserPendingChallengesById(self, userId, challenge) -> str:
        pendingChallengesIds = [challenge["id"] for challenge in self.lbUsersTable.find({'id': userId})[0]["pendingChallenges"]]
        updateResult = None
        userPendingMandatoryChallengesCount = self.lbUsersTable.count_documents({'id': userId, 'pendingChallenges': {'$elemMatch': {'isMandatory': True}}})
        if 3 - (len(pendingChallengesIds) - userPendingMandatoryChallengesCount) < 2 and challenge["isMandatory"] == False:
            raise Exception('User has the maximum number of non-mandatory pending challenges')
        if challenge["isMandatory"] == True:
            # userPendingMandatoryChallenges = self.lbUsersTable.find({'id': userId}, {'pendingChallenges': {'$elemMatch': {'isMandatory': True}}})
            if userPendingMandatoryChallengesCount == 0:
                challenge["id"] = 1
                updateResult = self.lbUsersTable.update_one({'id': userId}, {'$push': {'pendingChallenges': challenge}})
            elif userPendingMandatoryChallengesCount == 1:
                pendingChallengesIds = [challenge["id"] for challenge in self.lbUsersTable.find({'id': userId})[0]["pendingChallenges"]]
                maxPendingChallengeId = max(pendingChallengesIds)
                challenge["id"] = maxPendingChallengeId + 1
                updateResult = self.lbUsersTable.update_one({'id': userId}, {'$push': {'pendingChallenges': challenge}})
            else:
                raise Exception('User has the maximum number of pending mandatory challenges')
        if updateResult.modified_count == 1:
            return 'Challenge added to user pending challenges'
        else:
            raise Exception('User does not exist in leaderboard')
        
    def removeChallengeFromLeaderboardUserPendingChallengesById(self, userId, challengeId) -> dict:
        challengeToRemove = self.lbUsersTable.find({'id': userId}, {'pendingChallenges': {'$elemMatch': {'id': challengeId}}})[0]["pendingChallenges"][0]
        challengeToRemoveObject = ChallengeModelFromJSON(challengeToRemove)
        if challengeToRemoveObject.challenger.id == userId:
            updateResult = self.lbUsersTable.update_one({'id': challengeToRemoveObject.challenged.id}, {'$pull': {'pendingChallenges': {'challenger.id': userId}}})
        else:
            updateResult = self.lbUsersTable.update_one({'id': challengeToRemoveObject.challenger.id}, {'$pull': {'pendingChallenges': {'challenged.id': userId}}})
        updateResult = self.lbUsersTable.update_one({'id': userId}, {'$pull': {'pendingChallenges': {'id': challengeId}}})
        if updateResult.modified_count == 1:
            return challengeToRemoveObject
        else:
            raise Exception('User does not exist in leaderboard')
        
    def removeAllLeaderboardUserPendingChallengesById(self, userId) -> str:
        pendingChallenges = self.lbUsersTable.find({'id': userId}, {'pendingChallenges': 1})[0]["pendingChallenges"]
        for challenge in pendingChallenges:
            if challenge["challenger"]["id"] == userId:
                self.lbUsersTable.update_one({'id': challenge["challenged"]["id"]}, {'$pull': {'pendingChallenges': {'challenger.id': userId}}})
            else:
                self.lbUsersTable.update_one({'id': challenge["challenger"]["id"]}, {'$pull': {'pendingChallenges': {'challenged.id': userId}}})
        updateResult = self.lbUsersTable.update_one({'id': userId}, {'$set': {'pendingChallenges': []}})
        if updateResult.modified_count == 1:
            return 'All user pending challenges removed'
        else:
            raise Exception('User does not exist in leaderboard')
        
    def getChallengeStringFromLeaderboardUserPendingChallengesById(self, userId, challengeId) -> str:
        challenge = self.lbUsersTable.find_one({'id': userId}, {'pendingChallenges': {'$elemMatch': {'id': challengeId}}})
        return str(challenge)
    
    def getChallengeObjectFromLeaderboardUserPendingChallengesById(self, userId, challengeId) -> dict:
        challenge = self.lbUsersTable.find_one({'id': userId}, {'pendingChallenges': {'$elemMatch': {'id': challengeId}}})
        challengeObject = ChallengeModelFromJSON(challenge)
        return challengeObject
    
    def getChallengeDataFromLeaderboardUserPendingChallengesById(self, userId, challengeId) -> dict:
        challenge = self.lbUsersTable.find_one({'id': userId}, {'pendingChallenges': {'$elemMatch': {'id': challengeId}}})
        return challenge
    
    def getAllChallengeStringsFromLeaderboardUserPendingChallengesById(self, userId) -> list:
        challenges = self.lbUsersTable.find({'id': userId}, {'pendingChallenges': 1})[0]["pendingChallenges"]
        challengeObjects = [ChallengeModelFromJSON(challenge) for challenge in challenges]
        return [str(challenge) for challenge in challengeObjects]
    
    def getAllChallengeObjectsFromLeaderboardUserPendingChallengesById(self, userId) -> list:
        challenges = self.lbUsersTable.find({'id': userId}, {'pendingChallenges': 1})[0]["pendingChallenges"]
        return [ChallengeModelFromJSON(challenge) for challenge in challenges]
    
    def getAllChallengeDataFromLeaderboardUserPendingChallengesById(self, userId) -> list:
        return self.lbUsersTable.find({'id': userId}, {'pendingChallenges': 1})[0]["pendingChallenges"]
    
    def addChallengeToLeaderboardUserActiveChallengesById(self, userId, challenge) -> str:
        activeChallengesIds = [challenge["id"] for challenge in self.lbUsersTable.find({'id': userId})[0]["activeChallenges"]]
        maxActiveChallengeId = None
        try:
            maxActiveChallengeId = max(activeChallengesIds)
        except:
            maxActiveChallengeId = 0
        challenge["id"] = maxActiveChallengeId + 1
        updateResult = self.lbUsersTable.update_one({'id': userId}, {'$push': {'activeChallenges': challenge}})
        if updateResult.modified_count == 1:
            return 'Challenge added to user active challenges'
        else:
            raise Exception('User does not exist in leaderboard')
        
    def removeChallengeFromLeaderboardUserActiveChallengesById(self, userId, challengeId) -> str:
        challengeToRemove = self.lbUsersTable.find({'id': userId}, {'activeChallenges': {'$elemMatch': {'id': challengeId}}})[0]["activeChallenges"][0]
        updateResult = self.lbUsersTable.update_one({'id': userId}, {'$pull': {'activeChallenges': {'id': challengeId}}})
        if userId == challengeToRemove["challenger"]["id"]:
            self.lbUsersTable.update_one({'id': challengeToRemove["challenged"]["id"]}, {'$pull': {'activeChallenges': {'challenger.id': userId}}})
        else:
            self.lbUsersTable.update_one({'id': challengeToRemove["challenger"]["id"]}, {'$pull': {'activeChallenges': {'challenged.id': userId}}})
        if updateResult.modified_count == 1:
            return 'Challenge removed from user active challenges'
        else:
            raise Exception('User does not exist in leaderboard or challenge does not exist in user active challenges')
        
    def removeAllLeaderboardUserActiveChallengesById(self, userId) -> str:
        challengesToRemove = self.lbUsersTable.find({'id': userId}, {'activeChallenges': 1})[0]["activeChallenges"]
        updateResult = self.lbUsersTable.update_one({'id': userId}, {'$set': {'activeChallenges': []}})
        for challenge in challengesToRemove:
            if userId == challenge["challenger"]["id"]:
                self.lbUsersTable.update_one({'id': challenge["challenged"]["id"]}, {'$pull': {'activeChallenges': {'challenger.id': userId}}})
            else:
                self.lbUsersTable.update_one({'id': challenge["challenger"]["id"]}, {'$pull': {'activeChallenges': {'challenged.id': userId}}})
        if updateResult.modified_count == 1:
            return 'All user active challenges removed'
        else:
            raise Exception('User does not exist in leaderboard or user has no active challenges')
        
    def getChallengeStringFromLeaderboardUserActiveChallengesById(self, userId, challengeId) -> str:
        challenge = self.lbUsersTable.find_one({'id': userId}, {'activeChallenges': {'$elemMatch': {'id': challengeId}}})
        challengeObject = ChallengeModelFromJSON(challenge)
        return str(challengeObject)
    
    def getChallengeObjectFromLeaderboardUserActiveChallengesById(self, userId, challengeId) -> dict:
        challenge = self.lbUsersTable.find_one({'id': userId}, {'activeChallenges': {'$elemMatch': {'id': challengeId}}})
        challengeObject = ChallengeModelFromJSON(challenge)
        return challengeObject
    
    def getChallengeDataFromLeaderboardUserActiveChallengesById(self, userId, challengeId) -> dict:
        challenge = self.lbUsersTable.find_one({'id': userId}, {'activeChallenges': {'$elemMatch': {'id': challengeId}}})
        return challenge
    
    def getAllLeaderboardUserActiveChallengesStringsById(self, userId) -> str:
        activeChallenges = self.lbUsersTable.find_one({'id': userId})["activeChallenges"]
        activeChallengesStrings = []
        for challenge in activeChallenges:
            activeChallengeObject = ChallengeModelFromJSON(challenge)
            activeChallengesStrings.append(str(activeChallengeObject))
        return "\n".join(activeChallengesStrings)
    
    def getAllLeaderboardUserActiveChallengesObjectsById(self, userId) -> list:
        activeChallenges = self.lbUsersTable.find_one({'id': userId})["activeChallenges"]
        activeChallengesObjects = []
        for challenge in activeChallenges:
            activeChallengeObject = ChallengeModelFromJSON(challenge)
            activeChallengesObjects.append(activeChallengeObject)
        return activeChallengesObjects
    
    def getAllLeaderboardUserActiveChallengesDataById(self, userId) -> list:
        activeChallenges = self.lbUsersTable.find_one({'id': userId})["activeChallenges"]
        return activeChallenges
    
    # def getAllLeaderboardUserChallengeHistoryStringsById(self, userId) -> str:
    #     challengeHistory = self.lbUsersTable.find_one({'id': userId})["challengeHistory"]
    #     challengeHistoryStrings = []
    #     for challenge in challengeHistory:
    #         challengeObject = ChallengeModelFromJSON(challenge)
    #         challengeHistoryStrings.append(str(challengeObject))
    #     return "\n".join(challengeHistoryStrings)
    
    # def getAllLeaderboardUserChallengeHistoryObjectsById(self, userId) -> list:
    #     challengeHistory = self.lbUsersTable.find_one({'id': userId})["challengeHistory"]
    #     challengeHistoryObjects = []
    #     for challenge in challengeHistory:
    #         challengeObject = ChallengeModelFromJSON(challenge)
    #         challengeHistoryObjects.append(challengeObject)
    #     return challengeHistoryObjects
    
    # def getAllLeaderboardUserChallengeHistoryDataById(self, userId) -> list:
    #     challengeHistory = self.lbUsersTable.find_one({'id': userId})["challengeHistory"]
    #     return challengeHistory
        
    def addChallengeToLeaderboardUserChallengeHistoryById(self, userId, challenge) -> str:
        challengeHistroryIds = list(map(lambda x: x["id"], self.lbUsersTable.find({'id': userId})[0]["challengeHistory"]))
        maxChallengeId = None
        try:
            maxChallengeId = max(challengeHistroryIds)
        except:
            maxChallengeId = 0
        challenge["id"] = maxChallengeId + 1
        if len(challengeHistroryIds) != 2:
            updateResult = self.lbUsersTable.update_one({'id': userId}, {'$push': {'challengeHistory': challenge}, '$inc': {'challengeHistoryCount': 1}})
        else:
            removeChallenge = self.lbUsersTable.find_one({'id': userId}, {'challengeHistory': {'$slice': -1}})
            updateResult = self.lbUsersTable.update_one({'id': userId}, {'$push': {'challengeHistory': challenge}})
        if updateResult.modified_count == 1:
            return 'Challenge added to user challenge history'
        else:
            raise Exception('User does not exist in leaderboard')
        
    def removeChallengeFromLeaderboardUserChallengeHistoryById(self, userId, challengeId) -> str:
        updateResult = self.lbUsersTable.update_one({'id': userId}, {'$pull': {'challengeHistory': {'id': challengeId}}})
        if updateResult.modified_count == 1:
            return 'Challenge removed from user challenge history'
        else:
            raise Exception('User does not exist in leaderboard')
        
    def removeAllLeaderboardUserChallengeHistoryById(self, userId) -> str:
        updateResult = self.lbUsersTable.update_one({'id': userId}, {'$set': {'challengeHistory': []}})
        if updateResult.modified_count == 1:
            return 'All user challenge history removed'
        else:
            raise Exception('User does not exist in leaderboard')
        
    def getChallengeStringFromLeaderboardUserChallengeHistoryById(self, userId, challengeId) -> str:
        challenge = self.lbUsersTable.find_one({'id': userId}, {'challengeHistory': {'$elemMatch': {'id': challengeId}}})
        challengeObject = ChallengeResultModelFromJSON(challenge)
        return str(challengeObject)
    
    def getChallengeObjectFromLeaderboardUserChallengeHistoryById(self, userId, challengeId) -> dict:
        challenge = self.lbUsersTable.find_one({'id': userId}, {'challengeHistory': {'$elemMatch': {'id': challengeId}}})
        challengeObject = ChallengeResultModelFromJSON(challenge)
        return challengeObject
    
    def getChallengeDataFromLeaderboardUserChallengeHistoryById(self, userId, challengeId) -> dict:
        challenge = self.lbUsersTable.find_one({'id': userId}, {'challengeHistory': {'$elemMatch': {'id': challengeId}}})
        return challenge
    
    def getAllLeaderboardUserChallengeHistoryCountById(self, userId) -> int:
        return self.lbUsersTable.find({'id': userId})[0]["challengeHistoryCount"]
    
    def getAllLeaderboardUserChallengeHistoryStringsById(self, userId) -> str:
        challengeHistory = self.lbUsersTable.find_one({'id': userId})["challengeHistory"]
        challengeHistoryStrings = []
        for challenge in challengeHistory:
            challengeObject = ChallengeResultModelFromJSON(challenge)
            challengeHistoryStrings.append(str(challengeObject))
        return "\n".join(challengeHistoryStrings)
    
    def getAllLeaderboardUserChallengeHistoryObjectsById(self, userId) -> list:
        challengeHistory = self.lbUsersTable.find_one({'id': userId})["challengeHistory"]
        challengeHistoryObjects = []
        for challenge in challengeHistory:
            challengeObject = ChallengeResultModelFromJSON(challenge)
            challengeHistoryObjects.append(challengeObject)
        return challengeHistoryObjects
    
    def getAllLeaderboardUserChallengeHistoryDataById(self, userId) -> list:
        challengeHistory = self.lbUsersTable.find_one({'id': userId})["challengeHistory"]
        return challengeHistory
    
    def addLeaderboardModerator(self, moderator) -> str:
        # moderator = BSON.encode(moderator)
        insertResult = self.lbModeratorsTable.insert_one(moderator)
        if insertResult.inserted_id:
            return 'Moderator added to leaderboard'
        else:
            raise Exception('Moderator already exists in leaderboard')
        
    def removeLeaderboardModeratorById(self, moderatorId) -> str:
        changeResult = self.lbModeratorsTable.delete_one({'id': moderatorId})
        if changeResult.deleted_count == 1:
            return 'Moderator removed from leaderboard'
        else:
            raise Exception('Moderator does not exist in leaderboard')
        
    def removeAllLeaderboardModerators(self) -> str:
        changeResult = self.lbModeratorsTable.delete_many({})
        if changeResult.deleted_count > 0:
            return 'All moderators removed from leaderboard'
        else:
            raise Exception('No moderators exist in leaderboard')
        
    def getLeaderboardModeratorStringById(self, moderatorId) -> str:
        moderator = self.lbModeratorsTable.find_one({'id': moderatorId})
        moderatorObject = LBModeratorModelFromJSON(moderator)
        return str(moderatorObject)
    
    def getLeaderboardModeratorObjectById(self, moderatorId) -> dict:
        moderator = self.lbModeratorsTable.find_one({'id': moderatorId})
        moderatorObject = LBModeratorModelFromJSON(moderator)
        return moderatorObject
    
    def getLeaderboardModeratorDataById(self, moderatorId) -> dict:
        moderator = self.lbModeratorsTable.find_one({'id': moderatorId})
        return moderator
    
    def getAllLeaderboardModeratorStrings(self) -> str:
        moderators = self.lbModeratorsTable.find({})
        moderatorObjects = []
        for moderator in moderators:
            moderatorObject = LBModeratorModelFromJSON(moderator)
            moderatorObjects.append(str(moderatorObject))
        return "\n".join(moderatorObjects)
    
    def getAllLeaderboardModeratorObjects(self) -> list:
        moderators = self.lbModeratorsTable.find({})
        moderatorObjects = []
        for moderator in moderators:
            moderatorObject = LBModeratorModelFromJSON(moderator)
            moderatorObjects.append(moderatorObject)
        return moderatorObjects
    
    def getAllLeaderboardModeratorData(self) -> list:
        moderators = self.lbModeratorsTable.find({})
        return moderators