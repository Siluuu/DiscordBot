import asyncio
import json
import discord
from datetime import datetime
from discord.ext import commands
import app.style.better_print as better_print
import app.twitch.request as twitch_request
import app.logging as log
import os
from dotenv import load_dotenv

load_dotenv()


# clip management class
class Clip_Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.clip_list = None
        self.clip_dict_json = {}
        self.clip_dict = {}
        self.newest_clip_key = '0001.01.01_00:00:00'
        self.newest_clip = None
        self.clip_channel_id = os.getenv('CLIP_TEXT_CHANNEL_ID')


    # checks if a new clip was made
    async def check_clip(self):
        while True:
            try:
                try:
                    with open('json/twitch/clips.json', 'r') as old_clip_json:
                        self.clip_dict_json = json.load(old_clip_json)
                except (FileNotFoundError, json.JSONDecodeError):
                    log.log_info(f'[Discord] (clip_management.py) | Info | clips.json file missing or empty, initializing new clip_dict_json')
                    self.clip_dict_json = {}

                self.clip_list = twitch_request.get_clips()
                #log.log_info(f'[Discord] (clip_management.py) | Info | self.clip_list: {self.clip_list}')

                if self.clip_list:
                    for clip in self.clip_list[0]:
                        clip_title = clip['title']
                        clip_creator = clip['creator_name']
                        clip_url = clip['url']
                        clip_created_at = datetime.strptime(clip['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y.%m.%d_%H:%M:%S')

                        self.clip_dict[f'{clip_created_at}'] = {'title': f'{clip_title}', 'creator': f'{clip_creator}', 'url': f'{clip_url}'}

                    self.clip_dict = dict(sorted(self.clip_dict.items(), key=lambda item: datetime.strptime(item[0], '%Y.%m.%d_%H:%M:%S')))

                    #log.log_info(f'\n\n[Discord] (clip_management.py) | Info | self.clip_dict: {self.clip_dict}\n\n')
                    
                    latest_clip_key = list(self.clip_dict.keys())[-1]

                    log.logger.info(f'[Discord] (clip_management.py) | Info | latest_clip_key: {latest_clip_key}')
                    log.logger.info(f'[Discord] (clip_management.py) | Info | self.newest_clip_key: {self.newest_clip_key}')
                    log.logger.info(f'[Discord] (clip_management.py) | Info | self.newest_clip: {self.newest_clip}')

                    if self.newest_clip_key == '0001.01.01_00:00:00':
                        try:
                            self.newest_clip_key = list(self.clip_dict_json.keys())[-1]
                            self.newest_clip = self.clip_dict_json[self.newest_clip_key]
                        except:
                            self.newest_clip_key = '0001.01.01_00:00:00'

                    if datetime.strptime(latest_clip_key, '%Y.%m.%d_%H:%M:%S') > datetime.strptime(self.newest_clip_key, '%Y.%m.%d_%H:%M:%S'):
                        self.newest_clip_key = latest_clip_key
                        self.newest_clip = self.clip_dict[self.newest_clip_key]

                        await self.send_clip()

                        with open('json/twitch/clips.json', 'w') as new_clip_json:
                            json.dump(self.clip_dict, new_clip_json, indent=4)

                await asyncio.sleep(60)

            except Exception as err:
                error = f'[Discord] (clip_management.py) Error in check_clip: {err}'
                log.log_error(error)
                await asyncio.sleep(60)


    # sends the new clip to the discord channel
    async def send_clip(self):
        try:
            clip_title = self.newest_clip['title']
            clip_creator = self.newest_clip['creator']
            clip_url = self.newest_clip['url']

            channel = await self.bot.fetch_channel(self.clip_channel_id)
            await channel.send(f'**Clip created by {clip_creator}**\n*{clip_title}*\n{clip_url}')

        except Exception as err:
            error = f'[Discord] (clip_management.py) Error in send_clip: {err}'
            log.log_error(error)





    @commands.Cog.listener()
    async def on_ready(self):
        try:
            await asyncio.sleep(10)

            task1 = asyncio.create_task(self.check_clip())

            await asyncio.gather(task1)

        except Exception as err:
            error = f'[Discord] (clip_management.py) Error in on_ready: {err}'
            log.log_error(error)



def setup(bot):
    bot.add_cog(Clip_Management(bot))
