import 'package:lb_bot/secrets/secrets.dart';
import 'package:nyxx/nyxx.dart';

void main() {
  final bot = NyxxFactory.createNyxxWebsocket(secrets['token'],
      GatewayIntents.allUnprivileged | GatewayIntents.messageContent)
    ..registerPlugin(Logging()) // Default logging plugin
    ..registerPlugin(
        CliIntegration()) // Cli integration for nyxx allows stopping application via SIGTERM and SIGKILl
    ..registerPlugin(
        IgnoreExceptions()) // Plugin that handles uncaught exceptions that may occur
    ..connect();

  // Listen for message events
  bot.eventsWs.onMessageReceived.listen((event) async {
    if (event.message.content == "!ping" &&
        event.message.author.id != bot.self.id &&
        event.message.channel.id == Snowflake("1096523042248736798")) {
      await event.message.channel.sendMessage(MessageBuilder.content("Pong!"));
    }
  });
}
