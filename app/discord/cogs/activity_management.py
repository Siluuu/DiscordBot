import asyncio
import json
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import app.style.better_print as better_print
import app.twitch.request as twitch_request
import app.logging as log
import os
from dotenv import load_dotenv

load_dotenv()

class Activity_Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitch_channel_name = str(os.getenv('TWITCH_CHANNEL_NAME'))


    # updates the activity of the bot if a owner of the discord goes live or ended the stream
    async def update_activity(self):
        while True:
            try:
                is_live = twitch_request.get_streams()

                if is_live == True:
                    await self.bot.change_presence(activity=discord.Streaming(name=f'{self.twitch_channel_name} ist live!', url=f'https://www.twitch.tv/{self.twitch_channel_name.lower()}'))

                else:
                    filename = 'json/discord/counts.json'

                    with open(filename, 'r') as edging_file:
                        edging_streak = json.load(edging_file)

                    update_timed_str = edging_streak['edging_streak']['updated_time']
                    update_timed = datetime.strptime(update_timed_str, '%Y-%m-%d %H:%M:%S.%f')
                    edging_count = edging_streak['edging_streak']['edging_count']

                    now_time = datetime.now()
                    tomorrow_time = update_timed + timedelta(days=1)

                    #better_print.try_print(f'Now: {now_time}\nTomorrow: {tomorrow_time}\n')

                    if now_time >= tomorrow_time:
                        edging_count = edging_count + 1
                        edging_streak['edging_streak']['updated_time'] = tomorrow_time.strftime('%Y-%m-%d %H:%M:%S.%f')
                        edging_streak['edging_streak']['edging_count'] = edging_count

                        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f'Edging streak: Day {edging_count}'))

                        with open(filename, 'w') as edging_file:
                            json.dump(edging_streak, edging_file, indent=4)
                    elif edging_count == 0:
                        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f'Edging streak: Day 0'))
                    else:
                        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f'Edging streak: Day {edging_count}'))
                    
                await asyncio.sleep(60)

            except Exception as err:
                error = f'[Discord] (activity_management.py) Error in edging_streak: {err}'
                log.log_error(error)
                await asyncio.sleep(10)


    @commands.Cog.listener()
    async def on_ready(self):
        try:
            await asyncio.sleep(10)

            task1 = asyncio.create_task(Activity_Management.update_activity(self))
            await asyncio.gather(task1)

        except Exception as err:
            error = f'[Discord] (activty_management.py) Error in on_ready: {err}'
            log.log_error(error)





def setup(bot):
    bot.add_cog(Activity_Management(bot))
