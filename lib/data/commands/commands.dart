import 'package:lb_bot/bloc/cubits/user/lb_users_cubit.dart';
import 'package:lb_bot/data/models/user_models.dart';
import 'package:nyxx/nyxx.dart';
import 'package:nyxx_commands/nyxx_commands.dart';
import 'package:lb_bot/core/utils/elo/elo_calculator.dart';

ChatCommand ping = ChatCommand(
  "ping",
  "Pong!",
  (IChatContext context) {
    context.respond(MessageBuilder.content("Pong!"));
  },
);

ChatCommand eloTest = ChatCommand(
  "elo-test",
  "Calculates new rating",
  (IChatContext context, String rating, String opponentRating, String score) {
    // final elo = context.arguments;
    // print(elo.toString());
    // if (elo.length == 3) {
    try {
      double newRating = EloCalculator.newRatingFromScores(double.parse(rating),
          double.parse(opponentRating), double.parse(score));
      context.respond(MessageBuilder.content("New rating: $newRating"));
    } catch (e) {
      context.respond(MessageBuilder.content("Invalid command"));
    }
    // } else {
    //   context.respond(MessageBuilder.content("Invalid command"));
    // }
  },
);

LBUsersCubit lbUsersCubit = LBUsersCubit();

// LBUserCommands

ChatCommand lbAddUser = ChatCommand(
  "lb-add-user",
  "Adds a user to a leaderboard",
  (IChatContext context, IMember member, String name, bool mw2, bool bo2,
      bool isModerator) {
    List<Leaderboards> leaderboards = [];
    if (Leaderboards.values.contains(Leaderboards.mw2) &&
        Leaderboards.values.contains(Leaderboards.bo2)) {
      if (mw2) {
        leaderboards.add(Leaderboards.mw2);
      }
      if (bo2) {
        leaderboards.add(Leaderboards.bo2);
      }
      lbUsersCubit.addUser(
        LBUserModel(
            mw2Rating: 500,
            bo2Rating: null,
            matchHistory: [],
            activeChallenges: [],
            challengeHistory: [],
            id: member.id,
            name: name,
            isBanned: false,
            isModerator: isModerator,
            leaderboards: leaderboards,
            joined: DateTime.now(),
            lastActive: DateTime.now()),
      );
    }
    context.respond(MessageBuilder.content(
        'Added user named $name to leaderboard(s) ${leaderboards.map((e) => leaderboardToString(e)).join(", ")}'));
    print(lbUsersCubit.users.length);
  },
);
