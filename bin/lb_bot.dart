import 'dart:io';

import 'package:hydrated_bloc/hydrated_bloc.dart';
import 'package:lb_bot/core/utils/elo/elo_calculator.dart';
import 'package:lb_bot/data/commands/user_commands.dart';
import 'package:lb_bot/secrets/secrets.dart';
import 'package:nyxx/nyxx.dart';
import 'package:nyxx_commands/nyxx_commands.dart';
import 'package:nyxx_interactions/nyxx_interactions.dart';

Future<void> main() async {
  // setup hydrated bloc for desktop
  HydratedBloc.storage = await HydratedStorage.build(
    storageDirectory: Directory.current,
  );

  final bot = NyxxFactory.createNyxxWebsocket(secrets['token'],
      GatewayIntents.allUnprivileged | GatewayIntents.messageContent)
    ..registerPlugin(Logging()) // Default logging plugin
    ..registerPlugin(
        CliIntegration()) // Cli integration for nyxx allows stopping application via SIGTERM and SIGKILl
    ..registerPlugin(IgnoreExceptions());
  // Plugin that handles uncaught exceptions that may occur

  CommandsPlugin commands = CommandsPlugin(
      prefix: (message) => "/", // Prefix for commands
      guild: Snowflake('1096522707002196028'),
      options: CommandsOptions(
        logErrors: true,
      ));

  bot.registerPlugin(commands);

  commands.addCommand(ping);
  commands.addCommand(eloTest);
  commands.addCommand(lbAddUser);
  commands.addCommand(lbRemoveUser);
  commands.addCommand(lbUpdateUserName);
  commands.addCommand(lbFindUser);
  commands.addCommand(lbBanUser);
  commands.addCommand(lbUnbanUser);
  commands.addCommand(lbIsUserBanned);
  commands.addCommand(lbPromoteUser);
  commands.addCommand(lbDemoteUser);
  commands.addCommand(lbIsUserModerator);
  commands.addCommand(lbListAllUsers);

  IInteractions.create(WebsocketInteractionBackend(bot))
    ..registerSlashCommand(lbListLBUsers)
    ..registerSlashCommand(lbAddLeaderboard)
    ..registerSlashCommand(lbRemoveLeaderboard)
    ..syncOnReady();

  bot.connect();

  // Listen for message events
  // bot.eventsWs.onMessageReceived.listen((event) async {
  //   if (event.message.content == "!ping" &&
  //       event.message.author.id != bot.self.id &&
  //       event.message.channel.id == Snowflake("1096523042248736798")) {
  //     await event.message.channel.sendMessage(MessageBuilder.content("Pong!"));
  //   } else if (event.message.content.startsWith("!elo") &&
  //       event.message.author.id != bot.self.id &&
  //       event.message.channel.id == Snowflake("1096523042248736798")) {
  //     final elo = event.message.content.split(" ");
  //     if (elo.length == 4) {
  //       try {
  //         double newRating = EloCalculator.newRatingFromScores(
  //             double.parse(elo[1]), double.parse(elo[2]), double.parse(elo[3]));
  //         await event.message.channel
  //             .sendMessage(MessageBuilder.content("New rating: $newRating"));
  //       } catch (e) {
  //         await event.message.channel
  //             .sendMessage(MessageBuilder.content("Invalid command"));
  //       }
  //     } else {
  //       await event.message.channel
  //           .sendMessage(MessageBuilder.content("Invalid command"));
  //     }
  //   }
  // });
}
