import 'package:nyxx/nyxx.dart';

enum Leaderboards {
  mw2,
  bo2,
}

String leaderboardToString(Leaderboards leaderboard) {
  switch (leaderboard) {
    case Leaderboards.mw2:
      return 'mw2';
    case Leaderboards.bo2:
      return 'bo2';
  }
}

Leaderboards stringToLeaderboard(String leaderboard) {
  switch (leaderboard) {
    case 'mw2':
      return Leaderboards.mw2;
    case 'bo2':
      return Leaderboards.bo2;
    default:
      throw Exception('Invalid leaderboard string');
  }
}

class Challenge {
  DateTime challengeTime;
  LBUserModel challenger;
  LBUserModel challenged;
  Leaderboards leaderboard;
  bool isAccepted;
  bool isMandatory;
  DateTime expiryTime;

  Challenge({
    required this.challengeTime,
    required this.challenger,
    required this.challenged,
    required this.leaderboard,
    required this.isAccepted,
    required this.isMandatory,
    required this.expiryTime,
  });

  bool get isExpired => DateTime.now().isAfter(expiryTime);

  bool get isPending => !isAccepted && !isExpired;

  bool get isDeclined => !isAccepted && isExpired;

  bool get isActive => isAccepted && !isExpired;

  bool get isClosed => isAccepted && isExpired;

  // to json
  Map<String, dynamic> toJson() => {
        'challengeTime': challengeTime.toIso8601String(),
        'challenger': challenger.toJson(),
        'challenged': challenged.toJson(),
        'leaderboard': leaderboard.toString(),
        'isAccepted': isAccepted,
        'isMandatory': isMandatory,
        'expiryTime': expiryTime.toIso8601String(),
      };

  // from json
  factory Challenge.fromJson(Map<String, dynamic> json) => Challenge(
        challengeTime: DateTime.parse(json['challengeTime']),
        challenger: LBUserModel.fromJson(json['challenger']),
        challenged: LBUserModel.fromJson(json['challenged']),
        leaderboard: Leaderboards.values
            .firstWhere((e) => e.toString() == json['leaderboard']),
        isAccepted: json['isAccepted'],
        isMandatory: json['isMandatory'],
        expiryTime: DateTime.parse(json['expiryTime']),
      );
}

class Match {
  Challenge challenge;
  DateTime matchTime;
  DateTime closedTime;
  Snowflake winnerId;
  Snowflake loserId;
  String winnerName;
  String loserName;
  double winnerEloGain;
  double loserEloLoss;
  double winnerOldRating;
  double loserOldRating;
  double winnerNewRating;
  double loserNewRating;
  Leaderboards leaderboard;

  Match({
    required this.challenge,
    required this.matchTime,
    required this.closedTime,
    required this.winnerId,
    required this.loserId,
    required this.winnerName,
    required this.loserName,
    required this.winnerEloGain,
    required this.loserEloLoss,
    required this.winnerOldRating,
    required this.loserOldRating,
    required this.winnerNewRating,
    required this.loserNewRating,
    required this.leaderboard,
  });

  // to json
  Map<String, dynamic> toJson() => {
        'challenge': challenge.toJson(),
        'matchTime': matchTime.toIso8601String(),
        'closedTime': closedTime.toIso8601String(),
        'winnerId': winnerId.toString(),
        'loserId': loserId.toString(),
        'winnerName': winnerName,
        'loserName': loserName,
        'winnerEloGain': winnerEloGain,
        'loserEloLoss': loserEloLoss,
        'winnerOldRating': winnerOldRating,
        'loserOldRating': loserOldRating,
        'winnerNewRating': winnerNewRating,
        'loserNewRating': loserNewRating,
        'leaderboard': leaderboard.toString(),
      };

  // from json
  factory Match.fromJson(Map<String, dynamic> json) => Match(
        challenge: Challenge.fromJson(json['challenge']),
        matchTime: DateTime.parse(json['matchTime']),
        closedTime: DateTime.parse(json['closedTime']),
        winnerId: Snowflake(json['winnerId']),
        loserId: Snowflake(json['loserId']),
        winnerName: json['winnerName'],
        loserName: json['loserName'],
        winnerEloGain: json['winnerEloGain'],
        loserEloLoss: json['loserEloLoss'],
        winnerOldRating: json['winnerOldRating'],
        loserOldRating: json['loserOldRating'],
        winnerNewRating: json['winnerNewRating'],
        loserNewRating: json['loserNewRating'],
        leaderboard: Leaderboards.values
            .firstWhere((e) => e.toString() == json['leaderboard']),
      );
}

class BaseUserModel {
  Snowflake id;
  String name;
  bool isBanned;
  bool isModerator;
  List<Leaderboards> leaderboards;
  DateTime joined;
  DateTime lastActive;

  BaseUserModel({
    required this.id,
    required this.name,
    required this.isBanned,
    required this.isModerator,
    required this.leaderboards,
    required this.joined,
    required this.lastActive,
  });

  // to json
  Map<String, dynamic> toJson() => {
        'id': id.toString(),
        'name': name,
        'isBanned': isBanned,
        'isModerator': isModerator,
        'leaderboards': leaderboards.map((e) => e.toString()).toList(),
        'joined': joined.toIso8601String(),
        'lastActive': lastActive.toIso8601String(),
      };

  // from json
  factory BaseUserModel.fromJson(Map<String, dynamic> json) => BaseUserModel(
        id: Snowflake(json['id']),
        name: json['name'],
        isBanned: json['isBanned'],
        isModerator: json['isModerator'],
        leaderboards: List<String>.from(json['leaderboards'])
            .map((e) =>
                Leaderboards.values.firstWhere((e2) => e2.toString() == e))
            .toList(),
        joined: DateTime.parse(json['joined']),
        lastActive: DateTime.parse(json['lastActive']),
      );
}

class LBUserModel extends BaseUserModel {
  double? mw2Rating;
  double? bo2Rating;
  List<Match> matchHistory;
  List<Challenge> activeChallenges;
  List<Challenge> challengeHistory;

  LBUserModel({
    required this.mw2Rating,
    required this.bo2Rating,
    required this.matchHistory,
    required this.activeChallenges,
    required this.challengeHistory,
    required Snowflake id,
    required String name,
    required bool isBanned,
    required bool isModerator,
    required List<Leaderboards> leaderboards,
    required DateTime joined,
    required DateTime lastActive,
  }) : super(
          id: id,
          name: name,
          isBanned: isBanned,
          isModerator: isModerator,
          leaderboards: leaderboards,
          joined: joined,
          lastActive: lastActive,
        );

  // to json
  @override
  Map<String, dynamic> toJson() => {
        'mw2Rating': mw2Rating,
        'bo2Rating': bo2Rating,
        'matchHistory': matchHistory.map((e) => e.toJson()).toList(),
        'activeChallenges': activeChallenges.map((e) => e.toJson()).toList(),
        'challengeHistory': challengeHistory.map((e) => e.toJson()).toList(),
        ...super.toJson(),
      };

  // from json
  factory LBUserModel.fromJson(Map<String, dynamic> json) => LBUserModel(
        mw2Rating: json['mw2Rating'],
        bo2Rating: json['bo2Rating'],
        matchHistory: List<Map<String, dynamic>>.from(json['matchHistory'])
            .map((e) => Match.fromJson(e))
            .toList(),
        activeChallenges:
            List<Map<String, dynamic>>.from(json['activeChallenges'])
                .map((e) => Challenge.fromJson(e))
                .toList(),
        challengeHistory:
            List<Map<String, dynamic>>.from(json['challengeHistory'])
                .map((e) => Challenge.fromJson(e))
                .toList(),
        id: Snowflake(json['id']),
        name: json['name'],
        isBanned: json['isBanned'],
        isModerator: json['isModerator'],
        leaderboards: List<String>.from(json['leaderboards'])
            .map((e) =>
                Leaderboards.values.firstWhere((e2) => e2.toString() == e))
            .toList(),
        joined: DateTime.parse(json['joined']),
        lastActive: DateTime.parse(json['lastActive']),
      );
}

enum ModerationActions {
  ban,
  unban,
  warn,
  manageElo,
  manageChallenges,
  approveDeclines,
  manageMatchHistory,
  wipeAllData,
}

class ModerationAction {
  Snowflake moderatorId;
  Snowflake userId;
  ModerationActions action;
  DateTime time;
  String reason;

  ModerationAction({
    required this.moderatorId,
    required this.userId,
    required this.action,
    required this.time,
    required this.reason,
  });

  // to json
  Map<String, dynamic> toJson() => {
        'moderatorId': moderatorId.toString(),
        'userId': userId.toString(),
        'action': action.toString(),
        'time': time.toIso8601String(),
        'reason': reason,
      };

  // from json
  factory ModerationAction.fromJson(Map<String, dynamic> json) =>
      ModerationAction(
        moderatorId: Snowflake(json['moderatorId']),
        userId: Snowflake(json['userId']),
        action: ModerationActions.values
            .firstWhere((e) => e.toString() == json['action']),
        time: DateTime.parse(json['time']),
        reason: json['reason'],
      );
}

class LBModeratorModel extends BaseUserModel {
  List<Match> moderatedMatchHistory;
  List<Challenge> moderatedChallengeHistory;
  List<ModerationActions> abilities;
  List<ModerationAction> moderationHistory;

  LBModeratorModel({
    required this.moderatedMatchHistory,
    required this.moderatedChallengeHistory,
    required this.abilities,
    required this.moderationHistory,
    required Snowflake id,
    required String name,
    required bool isBanned,
    required bool isModerator,
    required List<Leaderboards> leaderboards,
    required DateTime joined,
    required DateTime lastActive,
  }) : super(
          id: id,
          name: name,
          isBanned: isBanned,
          isModerator: isModerator,
          leaderboards: leaderboards,
          joined: joined,
          lastActive: lastActive,
        );

  // to json
  @override
  Map<String, dynamic> toJson() => {
        'moderatedMatchHistory':
            moderatedMatchHistory.map((e) => e.toJson()).toList(),
        'moderatedChallengeHistory':
            moderatedChallengeHistory.map((e) => e.toJson()).toList(),
        'abilities': abilities.map((e) => e.toString()).toList(),
        'moderationHistory': moderationHistory.map((e) => e.toJson()).toList(),
        ...super.toJson(),
      };

  // from json
  factory LBModeratorModel.fromJson(Map<String, dynamic> json) =>
      LBModeratorModel(
        moderatedMatchHistory:
            List<Map<String, dynamic>>.from(json['moderatedMatchHistory'])
                .map((e) => Match.fromJson(e))
                .toList(),
        moderatedChallengeHistory:
            List<Map<String, dynamic>>.from(json['moderatedChallengeHistory'])
                .map((e) => Challenge.fromJson(e))
                .toList(),
        abilities: List<String>.from(json['abilities'])
            .map((e) =>
                ModerationActions.values.firstWhere((e2) => e2.toString() == e))
            .toList(),
        moderationHistory:
            List<Map<String, dynamic>>.from(json['moderationHistory'])
                .map((e) => ModerationAction.fromJson(e))
                .toList(),
        id: Snowflake(json['id']),
        name: json['name'],
        isBanned: json['isBanned'],
        isModerator: json['isModerator'],
        leaderboards: List<String>.from(json['leaderboards'])
            .map((e) =>
                Leaderboards.values.firstWhere((e2) => e2.toString() == e))
            .toList(),
        joined: DateTime.parse(json['joined']),
        lastActive: DateTime.parse(json['lastActive']),
      );
}
