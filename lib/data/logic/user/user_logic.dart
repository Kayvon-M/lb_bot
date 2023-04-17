import 'package:lb_bot/bloc/cubits/user/lb_users_cubit.dart';
import 'package:lb_bot/data/models/user_models.dart';

class UserLogic {
  static const int _ranksAbleToChallengeAbove = 4;
  static const int _ranksAbleToChallengeBelow = 2;

  List<LBUserModel> sortUsersByMw2Rating(List<LBUserModel> users) {
    List<LBUserModel> sortedUsers = [];
    for (var user in users) {
      if (user.mw2Rating != null && user.isBanned == false) {
        sortedUsers.add(user);
      }
    }
    sortedUsers.sort((a, b) => b.mw2Rating!.compareTo(a.mw2Rating!));
    return sortedUsers;
  }

  List<LBUserModel> sortUsersByBo2Rating(List<LBUserModel> users) {
    List<LBUserModel> sortedUsers = [];
    for (var user in users) {
      if (user.bo2Rating != null && user.isBanned == false) {
        sortedUsers.add(user);
      }
    }
    sortedUsers.sort((a, b) => b.bo2Rating!.compareTo(a.bo2Rating!));
    return sortedUsers;
  }

  bool canChallenge(LBUserModel challenger, LBUserModel challenged,
      Leaderboards leaderboard, List<LBUserModel> users) {
    if (leaderboard == Leaderboards.mw2) {
      List<LBUserModel> sortedUsers = sortUsersByMw2Rating(users);
      int challengerIndex = sortedUsers.indexOf(challenger);
      int challengedIndex = sortedUsers.indexOf(challenged);
      return challengerIndex - challengedIndex <= _ranksAbleToChallengeAbove &&
          challengedIndex - challengerIndex <= _ranksAbleToChallengeBelow;
    } else if (leaderboard == Leaderboards.bo2) {
      List<LBUserModel> sortedUsers = sortUsersByBo2Rating(users);
      int challengerIndex = sortedUsers.indexOf(challenger);
      int challengedIndex = sortedUsers.indexOf(challenged);
      return challengerIndex - challengedIndex <= _ranksAbleToChallengeAbove &&
          challengedIndex - challengerIndex <= _ranksAbleToChallengeBelow;
    } else {
      return false;
    }
  }

  Challenge createChallenge(LBUserModel challenger, LBUserModel challenged,
      Leaderboards leaderboard) {
    LBUsersCubit usersCubit = LBUsersCubit();
    bool canChallenge = this
        .canChallenge(challenger, challenged, leaderboard, usersCubit.users);
    if (canChallenge) {
      return Challenge(
          challengeTime: DateTime.now(),
          challenger: challenger,
          challenged: challenged,
          leaderboard: leaderboard,
          isAccepted: false,
          isMandatory: true,
          expiryTime: DateTime.now().add(Duration(days: 3)));
    } else {
      return Challenge(
          challengeTime: DateTime.now(),
          challenger: challenger,
          challenged: challenged,
          leaderboard: leaderboard,
          isAccepted: false,
          isMandatory: false,
          expiryTime: DateTime.now().add(Duration(days: 3)));
    }
  }
}
