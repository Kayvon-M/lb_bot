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

ChatCommand lbUpdateUserName = ChatCommand(
  "lb-update-user-name",
  "Updates a user's name",
  (IChatContext context, IMember member, String name) {
    try {
      String oldName = lbUsersCubit.updateUserName(member.id, name);
      context.respond(
          MessageBuilder.content('Updated user named $oldName to $name'));
      print(lbUsersCubit.users.length);
    } catch (e) {
      context.respond(MessageBuilder.content("Error: $e"));
    }
  },
);

ChatCommand lbFindUser = ChatCommand(
  "lb-find-user",
  "Finds a user by name",
  (IChatContext context, IMember member) {
    try {
      LBUserModel user = lbUsersCubit.getUser(member.id);
      context.respond(MessageBuilder.content(
          'Found user named ${user.name} with ID ${user.id}'));
      print(lbUsersCubit.users.length);
    } catch (e) {
      context.respond(MessageBuilder.content("Error: $e"));
    }
  },
);

ChatCommand lbBanUser = ChatCommand(
  "lb-ban-user",
  "Bans a user from all leaderboards",
  (IChatContext context, IMember member) {
    try {
      String bannedUserName = lbUsersCubit.banUser(member.id);
      context.respond(MessageBuilder.content(
          'Banned user named $bannedUserName from the leaderboards'));
      print(lbUsersCubit.users.length);
    } catch (e) {
      context.respond(MessageBuilder.content("Error: $e"));
    }
  },
);

ChatCommand lbUnbanUser = ChatCommand(
  "lb-unban-user",
  "Unbans a user from all leaderboards",
  (IChatContext context, IMember member) {
    try {
      String unbannedUserName = lbUsersCubit.unbanUser(member.id);
      context.respond(MessageBuilder.content(
          'Unbanned user named $unbannedUserName from the leaderboards'));
      print(lbUsersCubit.users.length);
    } catch (e) {
      context.respond(MessageBuilder.content("Error: $e"));
    }
  },
);

ChatCommand lbIsUserBanned = ChatCommand(
  "lb-is-user-banned",
  "Checks if a user is banned",
  (IChatContext context, IMember member) {
    try {
      bool isBanned = lbUsersCubit.isUserBanned(member.id);
      LBUserModel user = lbUsersCubit.getUser(member.id);
      context.respond(MessageBuilder.content(
          'User named ${user.name} is ${isBanned ? "" : "not "}banned'));
      print(lbUsersCubit.users.length);
    } catch (e) {
      context.respond(MessageBuilder.content("Error: $e"));
    }
  },
);

ChatCommand lbPromoteUser = ChatCommand(
  "lb-promote-user",
  "Promotes a user to moderator",
  (IChatContext context, IMember member) {
    try {
      String promotedUserName = lbUsersCubit.promoteUser(member.id);
      context.respond(MessageBuilder.content(
          'Promoted user named $promotedUserName to moderator'));
      print(lbUsersCubit.users.length);
    } catch (e) {
      context.respond(MessageBuilder.content("Error: $e"));
    }
  },
);

ChatCommand lbDemoteUser = ChatCommand(
  "lb-demote-user",
  "Demotes a user from moderator",
  (IChatContext context, IMember member) {
    try {
      String demotedUserName = lbUsersCubit.demoteUser(member.id);
      context.respond(MessageBuilder.content(
          'Demoted user named $demotedUserName from moderator'));
      print(lbUsersCubit.users.length);
    } catch (e) {
      context.respond(MessageBuilder.content("Error: $e"));
    }
  },
);

ChatCommand lbIsUserModerator = ChatCommand(
  "lb-is-user-moderator",
  "Checks if a user is a moderator",
  (IChatContext context, IMember member) {
    try {
      bool isModerator = lbUsersCubit.isUserModerator(member.id);
      LBUserModel user = lbUsersCubit.getUser(member.id);
      context.respond(MessageBuilder.content(
          'User named ${user.name} is ${isModerator ? "" : "not "}a moderator'));
      print(lbUsersCubit.users.length);
    } catch (e) {
      context.respond(MessageBuilder.content("Error: $e"));
    }
  },
);

final lbAddLeaderboard = SlashCommandBuilder(
    "lb-add-leaderboard", "Adds a user to a leaderboard", [
  CommandOptionBuilder(
      CommandOptionType.user, "user", "User to add to leaderboard",
      required: true),
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
    print(event.getArg("user").value);
    final userId = Snowflake(event.getArg("user").value as String);
    try {
      var name =
          lbUsersCubit.addLeaderboard(userId, stringToLeaderboard(leaderboard));
      await event.respond(MessageBuilder.content(
          "Added user $name to leaderboard $leaderboard"));
    } catch (e) {
      await event.respond(MessageBuilder.content("Error: $e"));
    }
  });

final lbRemoveLeaderboard = SlashCommandBuilder(
    "lb-remove-leaderboard", "Removes a user from a leaderboard", [
  CommandOptionBuilder(CommandOptionType.user, "user", "User to list",
      required: true),
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
    final userId = Snowflake(event.getArg("user").value as String);
    try {
      var name = lbUsersCubit.removeLeaderboard(
          userId, stringToLeaderboard(leaderboard));
      await event.respond(MessageBuilder.content(
          "Removed user $name from leaderboard $leaderboard"));
    } catch (e) {
      await event.respond(MessageBuilder.content("Error: $e"));
    }
  });

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
