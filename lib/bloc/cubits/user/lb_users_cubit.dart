import 'package:lb_bot/data/models/user_models.dart';
import 'package:hydrated_bloc/hydrated_bloc.dart';
import 'package:nyxx/nyxx.dart';

class LBUsersCubit extends HydratedCubit<List<LBUserModel>> {
  List<LBUserModel> get users => state;

  LBUsersCubit() : super([]);

  void addUser(LBUserModel user) {
    state.add(user);
    emit(state);
  }

  String removeUser(Snowflake id) {
    String username = state.firstWhere((user) => user.id == id).name;
    state.removeWhere((user) => user.id == id);
    emit(state);
    return username;
  }

  String updateUserName(Snowflake id, String newName) {
    String oldName = state.firstWhere((user) => user.id == id).name;
    state.firstWhere((user) => user.id == id).name = newName;
    emit(state);
    return oldName;
  }

  LBUserModel getUser(Snowflake id) {
    return state.firstWhere((user) => user.id == id);
  }

  String banUser(Snowflake id) {
    String username = state.firstWhere((user) => user.id == id).name;
    state.firstWhere((user) => user.id == id).isBanned = true;
    emit(state);
    return username;
  }

  String unbanUser(Snowflake id) {
    String username = state.firstWhere((user) => user.id == id).name;
    state.firstWhere((user) => user.id == id).isBanned = false;
    emit(state);
    return username;
  }

  bool isUserBanned(Snowflake id) {
    return state.firstWhere((user) => user.id == id).isBanned;
  }

  String promoteUser(Snowflake id) {
    String username = state.firstWhere((user) => user.id == id).name;
    state.firstWhere((user) => user.id == id).isModerator = true;
    emit(state);
    return username;
  }

  String demoteUser(Snowflake id) {
    String username = state.firstWhere((user) => user.id == id).name;
    state.firstWhere((user) => user.id == id).isModerator = false;
    emit(state);
    return username;
  }

  bool isUserModerator(Snowflake id) {
    return state.firstWhere((user) => user.id == id).isModerator;
  }

  String addLeaderboard(Snowflake id, Leaderboards leaderboard) {
    String username = state.firstWhere((user) => user.id == id).name;
    state.firstWhere((user) => user.id == id).leaderboards.add(leaderboard);
    if (leaderboard == Leaderboards.mw2) {
      state.firstWhere((user) => user.id == id).mw2Rating = 500;
    } else if (leaderboard == Leaderboards.bo2) {
      state.firstWhere((user) => user.id == id).bo2Rating = 500;
    }
    emit(state);
    return username;
  }

  String removeLeaderboard(Snowflake id, Leaderboards leaderboard) {
    String username = state.firstWhere((user) => user.id == id).name;
    state.firstWhere((user) => user.id == id).leaderboards.remove(leaderboard);
    if (leaderboard == Leaderboards.mw2) {
      state.firstWhere((user) => user.id == id).mw2Rating = null;
    } else if (leaderboard == Leaderboards.bo2) {
      state.firstWhere((user) => user.id == id).bo2Rating = null;
    }
    state.firstWhere((user) => user.id == id);
    emit(state);
    return username;
  }

  void changePlayerRating(
      Snowflake id, double newRating, Leaderboards leaderboard) {
    if (leaderboard == Leaderboards.mw2) {
      state.firstWhere((user) => user.id == id).mw2Rating = newRating;
    } else if (leaderboard == Leaderboards.bo2) {
      state.firstWhere((user) => user.id == id).bo2Rating = newRating;
    }
    emit(state);
  }

  void addMatchToHistory(Snowflake id, Match match) {
    state.firstWhere((user) => user.id == id).matchHistory.add(match);
    emit(state);
  }

  void removeMatchFromHistory(Snowflake id, Match match) {
    state.firstWhere((user) => user.id == id).matchHistory.remove(match);
    emit(state);
  }

  void addChallengeToHistory(Snowflake id, Challenge challenge) {
    state.firstWhere((user) => user.id == id).challengeHistory.add(challenge);
    emit(state);
  }

  void removeChallengeFromHistory(Snowflake id, Challenge challenge) {
    state
        .firstWhere((user) => user.id == id)
        .challengeHistory
        .remove(challenge);
    emit(state);
  }

  void addChallengeToActive(Snowflake id, Challenge challenge) {
    state.firstWhere((user) => user.id == id).activeChallenges.add(challenge);
    emit(state);
  }

  void removeChallengeFromActive(Snowflake id, Challenge challenge) {
    state
        .firstWhere((user) => user.id == id)
        .activeChallenges
        .remove(challenge);
    emit(state);
  }

  void updateLastActive(Snowflake id) {
    state.firstWhere((user) => user.id == id).lastActive = DateTime.now();
    emit(state);
  }

  @override
  List<LBUserModel> fromJson(Map<String, dynamic> json) {
    return (json['users'] as List).map((e) => LBUserModel.fromJson(e)).toList();
  }

  @override
  Map<String, dynamic> toJson(List<LBUserModel> state) {
    return {'users': state.map((e) => e.toJson()).toList()};
  }
}
