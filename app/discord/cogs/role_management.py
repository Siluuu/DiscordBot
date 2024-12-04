import asyncio
import json
import discord
from discord.ext import commands
import app.style.better_print as better_print
import app.twitch.request as twitch_request
import app.logging as log
import os
from dotenv import load_dotenv

load_dotenv()

class Role_Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = int(os.getenv('DISCORD_GUILD_ID'))


    # checks a user accepted or denied the account verification from the verification_respond.json
    async def new_verifications(self):
        async def wait_for_response(dc_name):
            while True:
                try:
                    filename = 'json/discord/verification_respond.json'
                    with open(filename, 'r') as respond_file:
                        user_respond = json.load(respond_file)
     
                    for username in user_respond:
                        if username == dc_name:
                            response = user_respond[f'{username}']
                            
                            user_respond.pop(username)
                            with open(filename, 'w') as respond_file:
                                json.dump(user_respond, respond_file, indent=4)

                            if response == '$accept':
                                return True
                            elif response == '$deny':
                                return False
                    
                    await asyncio.sleep(2)
                except Exception as err:
                    error = f'[Discord] (role_management.py) Error in wait_for_respond: {err}'
                    log.log_error(error)
                    await asyncio.sleep(10)


        # give the new role to the user
        async def add_role(guild, twitch_name, dc_name):
            try:
                twitch_mod_list = twitch_request.get_moderators()
                twitch_vip_list = twitch_request.get_vips()
                twitch_sub_list = twitch_request.get_broadcaster_supcriptions()

                role_list = []

                role = None
                second_role = None

                if twitch_name in twitch_mod_list:
                    role = 'Mod' 
                    if twitch_name in twitch_sub_list:
                        second_role = 'Subscriber'
                elif twitch_name in twitch_vip_list:
                    role = 'VIP'
                    if twitch_name in twitch_sub_list:
                        second_role = 'Subscriber'
                elif twitch_name in twitch_sub_list:
                    role = 'Subscriber'

                dc_user = discord.utils.get(guild.members, name=f'{dc_name}')

                if role != None:
                    await dc_user.add_roles(discord.utils.get(guild.roles, name=role))
                    role_list.append(role)
                    if second_role != None:
                        await dc_user.add_roles(discord.utils.get(guild.roles, name=second_role))
                        role_list.append(second_role)

                    role_count = len(role_list)
                    if role_count == 1:
                        await dc_user.send(f'Rolle hinzugefügt.')
                    else:
                        await dc_user.send(f'Rollen hinzugefügt.')

                filename = 'json/discord/verifyed_users.json'
                with open(filename ,'r') as verifyed_file:
                    verifyed_users = json.load(verifyed_file)

                verifyed_users[f'{dc_name}'] = {'id': f'{dc_user.id}', 'avatar_url': f'', 'roles': role_list, 'twitch': {'name': f'{twitch_name}', 'roles': role_list}}

                with open(filename ,'w') as verifyed_file:
                    json.dump(verifyed_users, verifyed_file, indent=4)

            except Exception as err:
                error = f'[Discord] (role_management.py) Error in add_role: {err}'
                log.log_error(error)
        

        # sends the user a dm
        async def send_dm(self, guild, twitch_name, dc_name):
            try:
                try:
                    dc_user = discord.utils.get(guild.members, name=f'{dc_name}')
                except:
                    error = f'[Discord] (role_management.py) Error in send_dm: Den User: {dc_name} gibt es nicht.'
                    log.log_error(error)
                    return
                
                await dc_user.send(f'**__Twitch verbinden__**\n'+
                                    f'\nMöchtest du deinen Twitch account: **{twitch_name}** mit deinen Discord verbinden, um Rollen auf dem LauchGang Server zu erhalten?\n'+
                                    f'\n`$accept` zum Verbinden oder `$deny` um den Vorgang abzubrechen.\n\nDu hast 10min Zeit!')
                
                try:
                    user_response = await asyncio.wait_for(wait_for_response(dc_name),timeout=600.0)
                except TimeoutError:
                    filename = 'json/discord/waiting_for_verification.json'
                    with open(filename, 'r') as waiting_file:
                        waiting_user = json.load(waiting_file)
                    waiting_user.pop(f'{twitch_name}')
                    with open(filename, 'w') as waiting_file:
                        json.dump(waiting_user, waiting_file, indent=4)
                    user_response = None

                if user_response == None or user_response == False:
                    await dc_user.send(f'Vorgang abgebrochen.\n\nDiese Nachrichten werden gleich gelöscht!')
                    message_count = 0
                    await asyncio.sleep(10)
                    dm_channel = await dc_user.create_dm()
                    async for message in dm_channel.history(limit=None):
                        if message.author == self.bot.user:
                            await message.delete()
                            message_count = message_count + 1
                            if message_count == 2:
                                return
                
                await add_role(guild, twitch_name, dc_name)  

            except Exception as err:
                error = f'[Discord] (role_management.py) Error in send_dm: {err}'
                log.log_error(error)


        guild = self.bot.get_guild(self.guild_id)
        while True:
            try:
                tasks = []
                remove_twitch_names = []

                try:
                    filename = 'json/discord/request_verification.json'
                    with open(filename, 'r') as request_file:
                        request_users = json.load(request_file)
                except:
                    request_users = {}

                for twitch_name in request_users:
                    dc_name = request_users[f'{twitch_name}']

                    waiting_user = {}
                    waiting_user[f'{twitch_name}'] = dc_name
                    with open('json/discord/waiting_for_verification.json', 'w') as wating_file:
                        json.dump(waiting_user, wating_file, indent=4)

                    remove_twitch_names.append(twitch_name)

                    tasks.append(asyncio.create_task(send_dm(self,guild,twitch_name,dc_name)))
                
                with open(filename, 'w') as request_file:
                        for twitch_name in remove_twitch_names:
                            request_users.pop(twitch_name)           
                        json.dump(request_users, request_file, indent=4)

                if len(tasks) != 0:
                    #better_print.try_print(f'[Discord] new verification task count: {len(tasks)}')
                    await asyncio.gather(*tasks)
                    
                await asyncio.sleep(5)

            except Exception as err:
                error = f'[Discord] (role_management.py) Error in new_verifications: {err}'
                log.log_error(error)
                await asyncio.sleep(60)
        

    # checks if a role status changed on twitch
    async def check_roles(self):
        guild = self.bot.get_guild(self.guild_id)
        while True:
            try:
                twitch_mod_list = twitch_request.get_moderators()
                twitch_vip_list = twitch_request.get_vips()
                twitch_sub_list = twitch_request.get_broadcaster_supcriptions()

                filename = f'json/discord/verifyed_users.json'
                with open(filename, 'r') as verifyed_file:
                    verifyed_users = json.load(verifyed_file)

                for dc_name in verifyed_users:
                    twitch_name = verifyed_users[f'{dc_name}']['twitch']['name']

                    twitch_roles = []
                    if twitch_name in twitch_mod_list:
                        twitch_roles.append('Mod')
                        if twitch_name in twitch_sub_list:
                            twitch_roles.append('Subscriber')
                    elif twitch_name in twitch_vip_list:
                        twitch_roles.append('VIP')
                        if twitch_name in twitch_sub_list:
                            twitch_roles.append('Subscriber')
                    elif twitch_name in twitch_sub_list:
                        twitch_roles.append('Subscriber')

                    try:
                        dc_user = discord.utils.get(guild.members, name=f'{dc_name}')
                    except Exception as err:
                        error = f'[Discord] (role_management.py) Error in check_roles: {err}'
                        log.log_error(error)
                        verifyed_users.pop(dc_name)
                        dc_user == None
                    
                    if dc_user != None:
                        dc_roles = []
                        all_dc_roles = []
                        for role in dc_user.roles:
                            role_name = role.name
                            all_dc_roles.append(role_name)
                            if role_name == 'Mod' or role_name == 'VIP' or role_name == 'Subscriber':
                                dc_roles.append(role_name)
                                if role_name not in twitch_roles:
                                    await dc_user.remove_roles(discord.utils.get(guild.roles, name=role_name))
                                    dc_roles.remove(role_name)
                                    await dc_user.send(f'Die Rolle **{role_name}** wurde entfernt.')

                        for new_role in twitch_roles:
                            if new_role not in dc_roles:
                                await dc_user.add_roles(discord.utils.get(guild.roles, name=new_role))
                                dc_roles.append(new_role)
                                await dc_user.send(f'Die Rolle **{new_role}** wurde hinzugefügt.')
                
                        log.logger.info(f'[Discord] (role_management.py) | Log | check_role: Discord name: {dc_user}, All Discord roles: {all_dc_roles}, ' + 
                                                                                            f'Twitch name: {twitch_name}, Twitch roles: {twitch_roles}')
                        
                        
                        verifyed_users[f'{dc_name}']['roles'] = all_dc_roles
                        verifyed_users[f'{dc_name}']['twitch']['roles'] = twitch_roles
                        verifyed_users[f'{dc_name}']['avatar_url'] = dc_user.display_avatar.url

                    with open(filename, 'w') as verifyed_file:
                        json.dump(verifyed_users, verifyed_file, indent=4)

                await asyncio.sleep(3600)
            except Exception as err:
                error = f'[Discord] (role_management.py) Error in check_roles: {err}'
                log.log_error(error)
                await asyncio.sleep(60)



    @commands.Cog.listener()
    async def on_ready(self):
        try:
            await asyncio.sleep(10)

            task1 = asyncio.create_task(Role_Management.new_verifications(self))
            task2 = asyncio.create_task(Role_Management.check_roles(self))

            await asyncio.gather(task1, task2)

        except Exception as err:
            error = f'[Discord] (role_management.py) Error in on_ready: {err}'
            log.log_error(error)


    # if the user send an $accept or $deny in the dms it saves it to verification_respond.json
    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if isinstance(message.channel, discord.DMChannel):
                user_name = f'{message.author.name}'
                user_message = f'{message.content}' 

                dc_name_list = [] 

                with open('json/discord/waiting_for_verification.json', 'r') as waiting_file:
                    waiting_users = json.load(waiting_file)

                for twitch_name in waiting_users:
                    dc_name = waiting_users[f'{twitch_name}']
                    dc_name_list.append(dc_name)

                if user_name in dc_name_list:
                    if user_message == '$accept' or user_message == '$deny':
                        user_respond = {}
                        user_respond[f'{user_name}'] = f'{user_message}'
                        with open('json/discord/verification_respond.json', 'w') as respond_file:
                            json.dump(user_respond, respond_file, indent=4)
                        
                        waiting_users.pop(twitch_name)
                        with open('json/discord/waiting_for_verification.json', 'w') as waiting_file:
                            json.dump(waiting_users, waiting_file, indent=4)

        except Exception as err:
            error = f'[Discord] (role_management.py) Error in on_message: {err}'
            log.log_error(error)




def setup(bot):
    bot.add_cog(Role_Management(bot))
