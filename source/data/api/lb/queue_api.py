# import json
# import random
# import discord

# from discord.ext import commands
# from discord import app_commands

# # Load config
# with open('source/config/config.json') as f:
#     config = json.load(f)


# class QueueApi(commands.Cog):
#     def __init__(self, client, max_players=8):
#         self.client = client
#         self.qcount = 0
#         self.team1 = []
#         self.team2 = []
#         self.total = []
#         self.mention = []
#         self.max_players = max_players

#     @app_commands.command(name='queue', description='Queue for a game', guild=discord.Object(id=config['guildId']))
#     @app_commands.choices(team=[
#         app_commands.Choice(name='Team 1', value='team1'),
#         app_commands.Choice(name='Team 2', value='team2')
#     ])
#     async def queue(self, ctx, team: str):
#         await ctx.defer()
#         if self.qcount < self.max_players:
#             if team == 'team1':
#                 self.team1.append(ctx.author)
#                 self.total.append(ctx.author)
#                 self.qcount += 1
#                 # await ctx.followup.send(f'{ctx.author.mention} has joined Team 1')
#             elif team == 'team2':
#                 self.team2.append(ctx.author)
#                 self.total.append(ctx.author)
#                 self.qcount += 1
#                 # await ctx.followup.send(f'{ctx.author.mention} has joined Team 2')
#             else:
#                 await ctx.followup.send('Invalid team')
#                 return
#             if self.qcount != self.max_players:
#                 await ctx.followup.send(f'{ctx.author.mention} has joined {team}')
#             else:
#                 hostOfGame = random.choice(self.total)
#                 password = random.randint(1000, 9999)
#                 await ctx.channel.send(f'{hostOfGame.mention} is the host of the game')
#                 await ctx.channel.send(f'Team 1: {self.team1}')
#                 await ctx.channel.send(f'Team 2: {self.team2}')
#                 HostEmbed = discord.Embed(
#                     title = f'{self.max_players}Mans',
#                     description = 'You\'re the host so create the lobby and let the other team know once the lobby is up.\n ' + '**Lobby Name:**  OU' + hostOfGame + '\n' + '**Password:** OU' + password,
#                     colour = discord.Colour.green()
#                 )
#                 Team1Embed = discord.Embed(
#                     title = f'{self.max_players}Mans',
#                     description = '**Host:** ' + f'{p}\n' + 'You\'re on the blue team, please keep an eye on the 6mans channel for an update from the host as to when the lobby is up.\n' + '**Lobby Name:** OU ' + hostOfGame + '\n' + '**Password:** OU' + password,
#                     colour = discord.Colour.blue()
#                 )
#                 Team2Embed = discord.Embed(
#                     title = f'{self.max_players}Mans',
#                     description = '**Host:** ' + f'{p}\n' + 'You\'re on the orange team, please keep an eye on the 6mans channel for an update from the host as to when the lobby is up.\n' + '**Lobby Name:** OU ' + hostOfGame + '\n' + '**Password:** OU' + password,
#                     colour = discord.Colour.orange()
#                 )
#                 for p in self.team1:
#                     await p.send(embed=Team1Embed)
#                 for p in self.team2:
#                     await p.send(embed=Team2Embed)
#                 await hostOfGame.send(embed=HostEmbed)
#                 overwrites = {
#                     ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
#                     ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
#                 }
#                 team1VC = await ctx.guild.create_voice_channel('Team 1', overwrites=overwrites)
#                 team2VC = await ctx.guild.create_voice_channel('Team 2', overwrites=overwrites)
#                 await team1VC.set_permissions(ctx.guild.default_role, connect=False)
#                 await team2VC.set_permissions(ctx.guild.default_role, connect=False)
#                 await team1VC.set_permissions(ctx.guild.me, connect=True)
#                 await team2VC.set_permissions(ctx.guild.me, connect=True)
#                 for p in self.team1:
#                     await team1VC.set_permissions(p, connect=True)
#                 for p in self.team2:
#                     await team2VC.set_permissions(p, connect=True)
#                 await ctx.channel.send(f'{team1VC.mention} and {team2VC.mention} have been created')
#                 await ctx.channel.send(f'**Lobby Name:** OU {hostOfGame}\n' + f'**Password:** OU {password}')
#                 self.qcount = 0
#                 self.team1 = []
#                 self.team2 = []
#                 self.total = []
#                 self.mention = []
#                 await ctx.followup.send('Start the game!')
#         else:
#             await ctx.followup.send('Queue is full')
        
#     @app_commands.command(name='leave', description='Leave the queue', guild=discord.Object(id=config['guildId']))
#     async def leave(self, ctx):
#         await ctx.defer()
#         if ctx.author in self.team1:
#             self.team1.remove(ctx.author)
#             self.total.remove(ctx.author)
#             self.qcount -= 1
#             await ctx.followup.send(f'{ctx.author.mention} has left the queue')
#         elif ctx.author in self.team2:
#             self.team2.remove(ctx.author)
#             self.total.remove(ctx.author)
#             self.qcount -= 1
#             await ctx.followup.send(f'{ctx.author.mention} has left the queue')
#         else:
#             await ctx.followup.send('You\'re not in the queue')

#     @app_commands.command(name='status', description='Check the status of the queue', guild=discord.Object(id=config['guildId']))
#     async def status(self, ctx):
#         await ctx.defer()
#         StatusEmbed = discord.Embed(
#             title = f'{self.qcount}/{self.max_players}',
#             description = f'Team 1: {self.team1}\n' + f'Team 2: {self.team2}',
#             colour = discord.Colour.blue()
#         )
#         await ctx.followup.send(embed=StatusEmbed)

#     @app_commands.command(name='remove', description='Remove a player from the queue', guild=discord.Object(id=config['guildId']))
#     async def remove(self, ctx, member: discord.Member):
#         await ctx.defer()
#         if member in self.team1:
#             self.team1.remove(member)
#             self.total.remove(member)
#             self.qcount -= 1
#             await ctx.followup.send(f'{member.mention} has been removed from the queue')
#         elif member in self.team2:
#             self.team2.remove(member)
#             self.total.remove(member)
#             self.qcount -= 1
#             await ctx.followup.send(f'{member.mention} has been removed from the queue')
#         else:
#             await ctx.followup.send('That player is not in the queue')

#     @app_commands.command(name='clear', description='Clear the queue', guild=discord.Object(id=config['guildId']))
#     async def clear(self, ctx):
#         await ctx.defer()
#         self.team1 = []
#         self.team2 = []
#         self.total = []
#         self.qcount = 0
#         await ctx.followup.send('Queue has been cleared')


# def setup(client):
#     client.add_cog(QueueApi(client))