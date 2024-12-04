import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import json
from datetime import datetime
import asyncio
import app.style.better_print as better_print
import app.twitch.request as twitch_requests
import app.logging as log
import os
from dotenv import load_dotenv

load_dotenv()

class Slash_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = int(os.getenv('DISCORD_GUILD_ID'))
        self.ylyl_submission_channel_id = int(os.getenv('YLYL_SUBMISSION_TEXT_CHANNEL_ID'))
        self.ylyl_approved_channel_id = int(os.getenv('YLYL_APPROVED_TEXT_CHANNEL_ID'))
        self.moderator_channel_id = int(os.getenv('MODERATOR_TEXT_CHANNEL_ID'))
        self.welcome_channel_id = int(os.getenv('WELCOME_TEXT_CHANNEL_ID'))


    # checks if the user is mod
    async def is_mod(self, username):
        try:
            log.log_info(f'DISCORD USERNAME: {username}')

            guild = self.bot.get_guild(self.guild_id)
            log.log_info(f'DISCORD GUILD: {guild}')

            user = discord.utils.get(guild.members, name=f'{username}')
            log.log_info(f'DISCORD USER: {user}')

            for role in user.roles:
                if role.name == 'Mod' or role.name == 'Owner':
                    return True
            return False

        except Exception as err:
            error = f'[Discord] (slash_commands.py) Error in is_mod: {err}'
            better_print.try_print(error)
            log.logger.info(error)
            

    # writes a message as the bot in the text channel
    @slash_command(description='Lass den Bot eine Nachricht senden (Mods only)')
    async def say(self, ctx, text: Option(str, 'test'), channel: Option(discord.TextChannel)):
        try:
            is_mod = await self.is_mod(ctx.author.name)
            if is_mod != True:
                await ctx.respond('Du hast nicht die nötigen berechtigungen dafür.', ephemeral=True)
                return
            
            await channel.send(text)
            await ctx.respond('Die Nachricht wurde gesendet', ephemeral=True)

        except Exception as err:
            error = f'[Discord] (slash_commands.py) Error in say: {err}'
            better_print.try_print(error)
            log.logger.info(error)


    # send information (account age, join age, profile picture and name) about a user to the text channel
    @slash_command(description='Information about a user /profile')
    async def profile(self, ctx, user: Option(discord.Member, 'Gib einen User an', default=None)):
        try:
            if user is None:
                user = ctx.author
                username = str(ctx.author.name)
            else:
                username = str(user)        

            erstellt = discord.utils.format_dt(user.created_at, 'R')
            beigetreten = discord.utils.format_dt(user.joined_at, 'R')

            embed = discord.Embed(
                    title=f'**{username}**',
                    color=discord.Color.purple()
                )

            embed.add_field(name='Erstellt', value=erstellt)
            embed.add_field(name='Beigetreten', value=beigetreten)

            embed.set_image(url=user.display_avatar.url)

            await ctx.respond(embed=embed)

        except Exception as err:
            error = f'[Discord] (slash_commands.py) Error in /profile: {err}'
            better_print.try_print(f'{error}')
            log.logger.info(error)
            await ctx.respond(error, ephemeral=True)


    # send a list of games that was requested and/or played to the text channel
    @slash_command(description='Spiele die Louis noch in Stream spielen muss.')
    async def games(self, ctx):
        try:

            try:
                filename ='json/twitch/pick_game.json'
                with open(filename, 'r') as save_file:
                    pick_game= json.load(save_file)
            except:
                await ctx.respond('Irgendwas ist schief gelaufen...\nProbiere es später erneut oder gebe einen Mod bescheid.')
                return

            await send_pick_games(ctx, pick_game)

        except Exception as err:
            error = f'[Discord] (slash_commands.py) Error in /games: {err}'
            log.log_error(error)


    # removes games from the games list
    @slash_command(description='Löscht ein Spiel aus der liste. (Mods only)')
    async def removegame(self, ctx, nummer: Option(str, 'Gib die Nummer des Spiels ein')):
        try:
            is_mod = await Slash_Commands.is_mod(self, ctx.author.name)
            if is_mod != True:
                await ctx.respond('Du hast nicht die nötigen berechtigungen dafür.', ephemeral=True)
                return
            
            try:
                filename ='json/twitch/pick_game.json'
                with open(filename, 'r') as save_file:
                    pick_game = json.load(save_file)
            except:
                await ctx.respond('Irgendwas ist schief gelaufen...')
            
            requested_games = pick_game['requested_games']
            game = requested_games[f'{nummer}']

            if nummer in pick_game['requested_games']:
                removed_game = requested_games.pop(nummer)

            for i, key in enumerate(sorted(requested_games.keys(), key=int)):
                requested_games[str(i + 1)] = requested_games.pop(key)

            with open(filename, 'w') as save_file:
                json.dump(pick_game, save_file, indent=4)

            await ctx.respond(f'{removed_game} wurde aus der liste entfernt.')

        except Exception as err:
            error = f'[Discord] (slash_commands.py) Error in /removegame: {err}'
            log.log_error(error)


    # sends a link to the ylyl text channel where a mod can approve it by reacting on it
    @slash_command(description='Submit ein Video für ylyl.')
    async def submit(self, ctx, link: Option(str, 'Füge hier den Videolink für ylyl ein')):
        try:
            # Check if link is blacklisted
            blacklist_file = 'json/discord/video_blacklist.json'
            try:
                with open(blacklist_file, 'r') as save_file:
                    video_blacklist = json.load(save_file)
            except FileNotFoundError:
                video_blacklist = {}

            if link in video_blacklist.values():
                await ctx.respond('Das Video ist auf der Blacklist.', ephemeral=True)
                return

            # Validate the link's format
            allowed_websites = [
                'https://www.youtube.com/watch?v=',
                'https://youtu.be/',
                'https://youtube.com/shorts/',
                'https://www.instagram.com/reel/',
                'https://www.instagram.com/p/',
                'https://www.tiktok.com/',
                'https://suno.com/song/',
                'https://soundcloud.com/'
            ]

            if not any(link.startswith(allowed) for allowed in allowed_websites):
                await ctx.respond('Du musst ein Link benutzen um etwas zu submitten. (Youtube, Twitch, Instagram, Tiktok, Suno)', ephemeral=True)
                return

            # Submit the video
            username = ctx.author.name
            channel = await self.bot.fetch_channel(self.ylyl_submission_channel_id)
            message = await channel.send(f'**Requested by {ctx.author.mention}**\n{link}')
            await message.add_reaction('\U00002705')
            await message.add_reaction('\U0000274C')

            # Respond to the user
            await ctx.respond('Dein Video wurde erfolgreich eingereicht.', ephemeral=True)

            # Save the submission
            filename = 'json/discord/video_submittedlist.json'
            try:
                with open(filename, 'r') as save_file:
                    video_submittedlist = json.load(save_file)
            except FileNotFoundError:
                video_submittedlist = {'submissions': {}, 'first_submit': False}

            video_submittedlist['submissions'][str(message.id)] = {"name": username, "link": link}
            video_submittedlist['first_submit'] = True

            with open(filename, 'w') as save_file:
                json.dump(video_submittedlist, save_file, indent=4)

            # Start checking submissions if not already running
            if video_submittedlist['first_submit']:
                asyncio.create_task(self.check_submissions())  # Correct way to start an async task

        except Exception as err:
            error = f'[Discord] (slash_commands.py) Error in /submit: {err}'
            log.log_error(error)
            await ctx.respond(error, ephemeral=True)


    # checks if the submissions were approved
    async def check_submissions(self):
        checkM = '\U00002705'
        cross = '\U0000274C'

        while True:
            try:
                # Load the video submissions JSON file
                filename = 'json/discord/video_submittedlist.json'
                try:
                    with open(filename, 'r') as save_file:
                        video_submittedlist = json.load(save_file)
                except FileNotFoundError:
                    log.log_error('[Discord] (slash_commands.py) Error in check_submissions: video_submittedlist.json not found.')
                    break

                message_ids = list(video_submittedlist.get('submissions', {}).keys())
                if not message_ids:
                    video_submittedlist['first_submit'] = False
                    with open(filename, 'w') as save_file:
                        json.dump(video_submittedlist, save_file, indent=4)
                    break

                # Iterate through messages and process reactions
                for message_id in message_ids:
                    try:
                        channel = await self.bot.fetch_channel(self.ylyl_submission_channel_id)
                        msg = await channel.fetch_message(int(message_id))
                        reactions = msg.reactions

                        for reaction in reactions:
                            if reaction.emoji not in [checkM, cross]:
                                continue

                            async for reaction_user in reaction.users():
                                user = reaction_user
                                is_mod = await self.is_mod(str(user))

                                if is_mod:
                                    submission = video_submittedlist['submissions'][message_id]

                                    if reaction.emoji == checkM:
                                        # Send to approved channel
                                        approved_channel = await self.bot.fetch_channel(self.ylyl_approved_channel_id)
                                        await approved_channel.send(
                                            f"**Requested by ||{submission['name']}||**\nApproved by {user}\n||{submission['link']}||"
                                        )
                                        video_submittedlist['submissions'].pop(message_id)

                                    elif reaction.emoji == cross:
                                        # Add to blacklist
                                        blacklist_file = 'json/discord/video_blacklist.json'
                                        try:
                                            with open(blacklist_file, 'r') as blacklist:
                                                video_blacklist = json.load(blacklist)
                                        except FileNotFoundError:
                                            video_blacklist = {}

                                        next_key = str(max(map(int, video_blacklist.keys()), default=0) + 1)
                                        video_blacklist[next_key] = submission['link']

                                        with open(blacklist_file, 'w') as blacklist:
                                            json.dump(video_blacklist, blacklist, indent=4)

                                        video_submittedlist['submissions'].pop(message_id)

                                    # Save updated submissions list
                                    with open(filename, 'w') as save_file:
                                        json.dump(video_submittedlist, save_file, indent=4)

                                    break

                    except discord.NotFound:
                        log.log_error(f'[Discord] (slash_commands.py) Error in check_submissions: Message with ID {message_id} not found. Removing from submissions.')
                        video_submittedlist['submissions'].pop(message_id, None)

            except Exception as err:
                log.log_error(f'[Discord] (slash_commands.py) Error in check_submissions: {err}')
                break

        await asyncio.sleep(1)


    # add a link to the blacklist, that should not be sending to the ylyl text channel
    @slash_command(description='Fügt ein Video in die ylyl blacklist hinzu (Mods only)')
    async def blacklist(self, ctx, link: Option(str, 'Füge hier den Videolink ein')):
        try:
            is_mod = await self.is_mod(ctx.author.name)
            if is_mod != True:
                await ctx.respond('Du hast nicht die nötigen berechtigungen dafür.', ephemeral=True)
                return

            try:
                filename_2 ='json/discord/video_blacklist.json'
                with open(filename_2, 'r') as save_file:
                    video_blacklist = json.load(save_file)
            except:
                video_blacklist = {}

            for i in video_blacklist:
                blacklist_link = video_blacklist[i]
                if link == blacklist_link:
                    await ctx.respond('Das Video ist schon auf der Blacklist', ephemeral=True)
                    return
                
            next_key = str(max(map(int, video_blacklist.keys()), default=0) + 1)
            video_blacklist[next_key] = link

            with open(filename_2, 'w') as save_file:
                json.dump(video_blacklist, save_file, indent=4)
        
        except Exception as err:
            error = f'[Discord] (slash_commands.py) Error in blacklist: {err}'
            log.log_error(error)


    # sends an embed to the text channel with stats from the twitch channel 
    @slash_command(description='Twitch Stats')
    async def stats(self, ctx):
        try:
            is_mod = await self.is_mod(ctx.author.name)
            if is_mod != True:
                await ctx.respond('Du hast nicht die nötigen berechtigungen dafür.', ephemeral=True)
                return
            else:
                await ctx.respond(f'Die Stats folgen in kürze.', ephemeral=True)

            channel = await self.bot.fetch_channel(self.moderator_channel_id)

            total_mods = len(twitch_requests.get_moderators())
            total_vips = len(twitch_requests.get_vips())
            total_subscriber = len(twitch_requests.get_broadcaster_supcriptions())
            total_follower = len(twitch_requests.get_channel_followers())
            #twitch_chatter_list = twitch_requests.get_channel_chatters()

            embed = discord.Embed(
                title='**Twitch Stats**',
                color=discord.Color.random()
            )
            embed.add_field(name='Mods', value=f'{total_mods}', inline=False)
            embed.add_field(name='Vips', value=total_vips, inline=False)
            embed.add_field(name='Subs', value=f'{total_subscriber}', inline=False)
            embed.add_field(name='Followers', value=f'{total_follower}', inline=False)

            today = datetime.now().strftime('%d.%m.%Y')
            embed.set_footer(text=f'Stand {today}')
            await channel.send(embed=embed)
        
        except Exception as err:
            error = f'[Discord] (slash_commands.py) Error in stats: {err}'
            log.log_error(error)


    # delete the dms from the bot
    @slash_command(description='Löscht alle Nachrichten in den DMs')
    async def cleardms(self, ctx, anzahl: Option(int, 'Wie viele Nachrichten sollen gelöscht werden?', default=None)):
        try:
            message_count = 0

            user_id = ctx.author.id
            user = await self.bot.fetch_user(user_id)
            await ctx.respond(f'Die Bot nachrichten werden gelöscht.', ephemeral=True)

            dm_channel = await user.create_dm()
            async for message in dm_channel.history(limit=None):
                if message.author == self.bot.user:
                    message_count = message_count + 1
                    await message.delete()
                    if message_count == anzahl:
                        return
                    #better_print.try_print(f"Deleted message: {message.content}")
                                    
        except Exception as err:
            error = f'[Discord] (slash_commands.py) Error in cleardm: {err}'
            log.log_error(error)
            

    # clears the video_submittedlist.json submission at the start of bot
    @commands.Cog.listener()
    async def on_ready(self):
        try:
            try:
                filename = 'json/discord/video_submittedlist.json'
                with open(filename, 'r') as save_file:
                    video_submittedlist = json.load(save_file)
            except:
                video_submittedlist = {}

            video_submittedlist['submissions'] = {}
            video_submittedlist['first_submit'] = False

            with open(filename, 'w') as save_file:
                json.dump(video_submittedlist, save_file, indent=4)

        except Exception as err:
            error = f'[Discord] (slash_commands.py) Error in on_ready: {err}'
            log.log_error(error)


    # sends a welcome message to the general text channel
    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            embed = discord.Embed(
                title='Willkommen',
                description=f'Hey {member.mention}',
                color=discord.Color.dark_green()
            )

            embed.add_field(name=' ', value='Willkommen in der Lauchgang!', inline=False)
            embed.set_image(url=member.display_avatar.url)

            channel = await self.bot.fetch_channel(self.welcome_channel_id)
            await channel.send(embed=embed)

        except Exception as err:
            error = f'[Discord] (slash_commands.py) Error in on_member_join: {err}'
            log.log_error(error)



# creates the embed for the /stats command
class Paginator(discord.ui.View):
    def __init__(self, followers, author, per_page=25):
        super().__init__()
        self.followers = followers
        self.author = author
        self.per_page = per_page
        self.current_page = 0
        self.total_pages = (len(followers) - 1) // per_page + 1


    def create_embed(self):
        embed = discord.Embed(
            title='**Follower**',
            color=discord.Color.random()
        )
        embed.set_footer(text=f'*Requested by {self.author}')
        start = self.current_page * self.per_page
        end = start + self.per_page
        for i, username in enumerate(self.followers[start:end], start=start + 1):
            embed.add_field(name='', value=f'**{i}** {username}', inline=False)
        embed.set_footer(text=f'Page {self.current_page + 1}/{self.total_pages} • Requested by {self.author}')
        return embed


    @discord.ui.button(label='<---', style=discord.ButtonStyle.primary)   #Voher
    async def previous(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
        if self.current_page < 0:
            self.current_page = self.total_pages -1
        await interaction.response.edit_message(embed=self.create_embed(), view=self)


    @discord.ui.button(label='--->', style=discord.ButtonStyle.primary)   #Nächster
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
        if self.current_page > self.total_pages - 1:
            self.current_page -= 1
        await interaction.response.edit_message(embed=self.create_embed(), view=self)


async def send_follower_list(channel, message_author, twitch_follower_list):
    view = Paginator(twitch_follower_list, message_author)
    await channel.send(embed=view.create_embed(), view=view)



# creates the embed for the /games command
class Games_Paginator(discord.ui.View):
    def __init__(self, pick_game, per_page=25):
        super().__init__()
        self.pick_game = pick_game
        self.per_page = per_page
        self.current_view = 'requested'  # 'requested' or 'played'

        # Track pages for both views
        self.page_positions = {'requested': 0, 'played': 0}

        # Calculate total pages for non-empty lists only
        self.total_pages_requested = ((len(pick_game['requested_games']) - 1) // per_page + 1 
                                      if pick_game['requested_games'] else 0)
        self.total_pages_played = ((len(pick_game['played_games']) - 1) // per_page + 1 
                                   if pick_game['played_games'] else 0)

        # Total combined pages
        self.total_pages = self.total_pages_requested + self.total_pages_played

    def create_embed(self):
        # Decide title and list based on current_view
        if self.current_view == 'requested':
            games_list = list(self.pick_game['requested_games'].values())
            title = "**Games to play**"
            color = discord.Color.green()
            offset = 0
        else:
            games_list = list(self.pick_game['played_games'].values())
            title = "**Played games**"
            color = discord.Color.orange()
            offset = self.total_pages_requested

        # Calculate overall current page
        self.current_page = self.page_positions[self.current_view] + 1 + offset

        embed = discord.Embed(
            title=title,
            color=color
        )

        # Paginate the games
        start = self.page_positions[self.current_view] * self.per_page
        end = start + self.per_page

        for i, game in enumerate(games_list[start:end], start=start + 1):
            game_str = f'**{i}** - {game}'
            embed.add_field(name='', value=game_str, inline=False)

        embed.set_footer(text=f'Page: {self.current_page}/{self.total_pages}')

        return embed

    def switch_view(self, direction):
        """Switch to the next view based on direction."""
        if self.current_view == 'requested':
            self.current_view = 'played'
        else:
            self.current_view = 'requested'

        # Update page position for the new view
        if direction == "next":
            self.page_positions[self.current_view] = 0
        elif direction == "previous":
            if self.current_view == 'requested':
                self.page_positions[self.current_view] = self.total_pages_requested - 1
            else:
                self.page_positions[self.current_view] = self.total_pages_played - 1

    @discord.ui.button(label='<---', style=discord.ButtonStyle.primary)
    async def previous(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.current_view == 'requested' and self.page_positions['requested'] > 0:
            # Move within the requested view
            self.page_positions['requested'] -= 1
        elif self.current_view == 'played' and self.page_positions['played'] > 0:
            # Move within the played view
            self.page_positions['played'] -= 1
        else:
            # Switch to the previous view
            self.switch_view("previous")

        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label='--->', style=discord.ButtonStyle.primary)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.current_view == 'requested' and self.page_positions['requested'] < self.total_pages_requested - 1:
            # Move within the requested view
            self.page_positions['requested'] += 1
        elif self.current_view == 'played' and self.page_positions['played'] < self.total_pages_played - 1:
            # Move within the played view
            self.page_positions['played'] += 1
        else:
            # Switch to the next view
            self.switch_view("next")

        await interaction.response.edit_message(embed=self.create_embed(), view=self)

async def send_pick_games(ctx, pick_game):
    await ctx.defer()
    view = Games_Paginator(pick_game)

    # Only show the view if at least one list is not empty
    if view.total_pages_requested > 0 or view.total_pages_played > 0:
        await ctx.respond(embed=view.create_embed(), view=view)
    else:
        await ctx.respond('Es gibt keine Spiele, die gespielt oder requested wurden', ephemeral=True)







def setup(bot):
    bot.add_cog(Slash_Commands(bot))
