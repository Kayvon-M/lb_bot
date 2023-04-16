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

  void updateUser(LBUserModel user) {
    state.removeWhere((u) => u.id == user.id);
    state.add(user);
    emit(state);
  }

  void banUser(Snowflake id) {
    state.firstWhere((user) => user.id == id).isBanned = true;
    emit(state);
  }

  void unbanUser(Snowflake id) {
    state.firstWhere((user) => user.id == id).isBanned = false;
    emit(state);
  }

  void promoteUser(Snowflake id) {
    state.firstWhere((user) => user.id == id).isModerator = true;
    emit(state);
  }

  void demoteUser(Snowflake id) {
    state.firstWhere((user) => user.id == id).isModerator = false;
    emit(state);
  }

  void addLeaderboard(Snowflake id, Leaderboards leaderboard) {
    state.firstWhere((user) => user.id == id).leaderboards.add(leaderboard);
    emit(state);
  }

  void removeLeaderboard(Snowflake id, Leaderboards leaderboard) {
    state.firstWhere((user) => user.id == id).leaderboards.remove(leaderboard);
    emit(state);
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
