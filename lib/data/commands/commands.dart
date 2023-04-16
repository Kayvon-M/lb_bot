import 'package:lb_bot/bloc/cubits/user/lb_users_cubit.dart';
import 'package:lb_bot/data/logic/user/user_logic.dart';
import 'package:lb_bot/data/models/user_models.dart';
import 'package:nyxx/nyxx.dart';
import 'package:nyxx_commands/nyxx_commands.dart';
import 'package:lb_bot/core/utils/elo/elo_calculator.dart';
import 'package:nyxx_interactions/nyxx_interactions.dart';

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
      if (mw2 && !bo2) {
        leaderboards.add(Leaderboards.mw2);
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
      } else if (bo2 && !mw2) {
        leaderboards.add(Leaderboards.bo2);
        lbUsersCubit.addUser(
          LBUserModel(
              mw2Rating: null,
              bo2Rating: 500,
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
      } else if (bo2 && mw2) {
        leaderboards.add(Leaderboards.bo2);
        leaderboards.add(Leaderboards.mw2);
        lbUsersCubit.addUser(
          LBUserModel(
              mw2Rating: 500,
              bo2Rating: 500,
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
    }
    context.respond(MessageBuilder.content(
        'Added user named $name to leaderboard(s) ${leaderboards.map((e) => leaderboardToString(e)).join(", ")}'));
    print(lbUsersCubit.users.length);
  },
);

ChatCommand lbRemoveUser = ChatCommand(
  "lb-remove-user",
  "Removes a user from all leaderboards",
  (IChatContext context, IMember member) {
    try {
      String removedUserName = lbUsersCubit.removeUser(member.id);
      context.respond(MessageBuilder.content(
          'Removed user named $removedUserName from the leaderboards'));
      print(lbUsersCubit.users.length);
    } catch (e) {
      context.respond(MessageBuilder.content("Error: $e"));
    }
  },
);

// ChatCommand lbListUsers = ChatCommand(
//   "lb-list-users",
//   "Lists all users",
//   (IChatContext context, String
//     context.respond(MessageBuilder.content(
//         lbUsersCubit.users.map((e) => e.name).join(", ")));
//   },
// );

final lbListAllUsers =
    SlashCommandBuilder("lb-list-users", "List all users in a leaderboard", [
  CommandOptionBuilder(
      CommandOptionType.string, "leaderboard", "Leaderboard to list users from",
      required: true,
      choices: [
        ArgChoiceBuilder("MW2", "mw2"),
        ArgChoiceBuilder("BO2", "bo2"),
      ]),
])
      ..registerHandler((event) async {
        final leaderboard = event.getArg("leaderboard").value as String;
        List<LBUserModel> users = [];
        UserLogic userLogic = UserLogic();
        if (leaderboard == "mw2") {
          try {
            users = userLogic.sortUsersByMw2Rating(lbUsersCubit.users);
          } catch (e) {
            event.respond(MessageBuilder.content("Error: $e"));
          }
        } else if (leaderboard == "bo2") {
          try {
            users = userLogic.sortUsersByBo2Rating(lbUsersCubit.users);
          } catch (e) {
            event.respond(MessageBuilder.content("Error: $e"));
          }
        }
        String usersString = users
            .map((e) => leaderboard == "mw2"
                ? "${e.name} - ${e.mw2Rating}"
                : "${e.name} - ${e.bo2Rating}")
            .join("\n");
        await event.respond(MessageBuilder.content(usersString));
      });
