import os
import discord
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import app.style.better_print as better_print
import app.logging as log

load_dotenv()

guild_id = int(os.getenv('DISCORD_GUILD_ID'))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot_token = os.getenv('DISCORD_TOKEN')

bot = discord.Bot(
    intents=intents,
    debug_guilds=[f'{guild_id}']
    )


@bot.event
async def on_ready():
    try:
        better_print.first_print()
        better_print.discord_bot_ready(bot.user)
        better_print.last_print()

        filename = 'json/discord/video_submittedlist.json'
        with open(filename, 'r') as save_file:
            video_submittedlist = json.load(save_file)
            
        video_submittedlist['first_submit'] = False

        with open(filename, 'w') as save_file:
            json.dump(video_submittedlist, save_file, indent=4)      

    except Exception as err:
        error = f'[Discord] Error in on_ready: {err}'
        log.log_error(error)


# logs every message that was send in the discord
@bot.event
async def on_message(message):
    try:
        time = datetime.now().strftime('%H:%M:%S')
        try:
            message_full = f'{time} - [Discord] Channel: {message.channel.name}, User: {message.author.name}, Message: {message.content}'
        except:
            if isinstance(message.channel, discord.DMChannel):
                message_full = f'[Discord] Channel: DM, User: {message.author.name}, Message: {message.content}'
            else:
                message_full = f'[Discord] Unknown message was send.'

        better_print.try_print(message_full)
        log.logger.info(message_full)
    except Exception as err:
        error = f'[Discord] Error in on_message: {err}'
        log.log_error(error)




# loads every extension in the ../cogs folder
for filename in os.listdir('app/discord/cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'app.discord.cogs.{filename[:-3]}')

def discord_bot_start():
    bot.run(bot_token)

if __name__ == '__main__':
    discord_bot_start()
