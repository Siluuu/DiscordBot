import os
import requests
import datetime
import app.twitch.oauth_2 as oauth
import app.logging as log
import app.style.better_print as better_print
import json
from datetime import datetime
from time import sleep
from dotenv import load_dotenv

load_dotenv()

CHANNEL_NAME = os.getenv('TWITCH_CHANNEL_NAME')
CHANNEL_ID = os.getenv('TWITCH_CHANNEL_ID')
CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')

modlist = []
game_name = ''

base_url = 'https://api.twitch.tv/helix'


# Fetch User ID from Twitch Username
def fetch_user_id(username):
    try:
        access_token = oauth.Oauth().get_last_tokens()

        url = f'{base_url}/users'
        HEADERS = {
            'Client-ID': CLIENT_ID,
            'Authorization': f'Bearer {access_token}'
        }
        params = {
            'login': username
        }

        response = requests.get(url,headers=HEADERS, params=params)
        data = response.json()
        #better_print.try_print(data)
        return data['data'][0]['id']
    except Exception as err:
        error = f'[Twitch Request] Error in fetch_user_id: {err}'
        log.log_error(error)


# Get Information from the Twitch Channel (language, game name, title, tags)
def get_channel_info():
    global game_name
    access_token = oauth.Oauth().get_last_tokens()

    try:
        url = f'{base_url}/channels?broadcaster_id={CHANNEL_ID}'
        HEADERS = {
            'Client-Id': CLIENT_ID,
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.get(url=url, headers=HEADERS)
        response_data = response.json()

        language = response_data['data'][0]['broadcaster_language']
        game_name = response_data['data'][0]['game_name']
        game_name = f'[{game_name}]'
        title = response_data['data'][0]['title']
        tags = response_data['data'][0]['tags']

        #better_print.try_print(response_data)
        #better_print.try_print(f'\nChannel Information:\n-Language: {language}\n-Game name: {game_name}\n-Title: {title}\n-Tags: {tags}\n')

        return game_name
    except Exception as err:
        error = f'[Twitch Request] Error in get_channel_info: {err}'
        log.log_error(error)


# Get a list of Twitch Channel Moderators
def get_moderators():
    access_token = oauth.Oauth().get_last_tokens()
    try:
        modlist = []

        url = f'{base_url}/moderation/moderators?broadcaster_id={CHANNEL_ID}'
        HEADERS = {
                'Client-Id': CLIENT_ID,
                'Authorization': f'Bearer {access_token}'
            }
        
        response = requests.get(url=url, headers=HEADERS)
        response_data = response.json()

        for i in response_data['data']:
            username = i['user_name']
            username = str(username).lower()
            modlist +=  [username]

        #better_print.try_print(f'modlist: {modlist}\n')
        #better_print.try_print(response_data['data'])
        return modlist
    except Exception as err:
        error = f'[Twitch Request] Error in get_moderators: {err}'
        log.log_error(error)


# Get a Boolean if the Twitch Channel is live
def get_streams():
    try:
        access_token = oauth.Oauth().get_last_tokens()

        url = f'{base_url}/streams?user_login={CHANNEL_NAME}'
        HEADERS = {
                'Client-Id': CLIENT_ID,
                'Authorization': f'Bearer {access_token}'
            }
        response = requests.get(url=url, headers=HEADERS)
        response_data = response.json()
        #better_print.try_print(response_data)
        if response_data['data'] == []:
            is_live = False
        else:
            is_live = True

        return is_live

    except Exception as err:
        error = f'[Twitch Request] Error in get_streams: {err}'
        log.log_error(error)
        sleep(10)


# Get the time how long the Twitch Channel is already live
def get_uptime(username):
    try:
        url = f'https://decapi.me/twitch/uptime/{username}'
        response = requests.get(url)
        uptime = response.text
        #better_print.try_print(f'uptime: {uptime}\n')
        if uptime == f'{username} is offline':
            uptime = f'{uptime}.'
        else:
            uptime = f'{username} ist online seit {uptime}.'

        return uptime
    except Exception as err:
        error = f'[Twitch Request] Error in get_uptime: {err}'
        log.log_error(error)


# Get a list of Usernames from People that watching the Twitch Channal live right now
def get_channel_chatters():
    access_token = oauth.Oauth().get_last_tokens()

    try:
        chatters_list = []

        url = f'{base_url}/chat/chatters?broadcaster_id={CHANNEL_ID}&moderator_id={CHANNEL_ID}&Ratelimit-Reset'
        HEADERS = {
                    'Client-Id': CLIENT_ID,
                    'Authorization': f'Bearer {access_token}'
                }
        
        response = requests.get(url,headers=HEADERS)
        response_data = response.json()

        #better_print.try_print(f'get_channel_chatters response: {response_data}')

        for username in response_data['data']:
            viewer = str(username['user_name']).lower()
            chatters_list.append(viewer)

        return chatters_list

    except Exception as err:
        error = f'[Twitch Request] Error in get_channel_chatters: {err}'
        log.log_error(error)

# Get a list of Username from People that following the Twitch Channel
def get_channel_followers():
    access_token = oauth.Oauth().get_last_tokens()

    try:
        last_page = False
        follower_list = []

        url = f'{base_url}/channels/followers?broadcaster_id={CHANNEL_ID}'
        HEADERS = {
            'Client-Id': CLIENT_ID,
            'Authorization': f'Bearer {access_token}'
        }
        params = {
            'first': 100
        }

        while last_page == False:

            response = requests.get(url, headers=HEADERS, params=params)
            response_data = response.json()
            #better_print.try_print(f'Response data: {response_data}')
            #better_print.try_print(f'get_channel_followers response: {response_data}')

            try:
                pagination = response_data['pagination']
                #better_print.try_print(f'Pagination: {pagination}\n')
            except:
                pagination = {}
            
            try:
                cursor = pagination['cursor']
                #better_print.try_print(f'Cursor: {cursor}\n')
            except:
                pass

            if pagination != {}:
                last_page = False
                params = {
                    'first': 100,
                    'after': cursor
                }
            else:
               last_page = True

            follower_count = response_data['total']
            #better_print.try_print(follower_count)

            for username in response_data['data']:
                viewer = str(username['user_name']).lower()
                follower_list.append(viewer)
        
        #better_print.try_print(f'Follower list: {follower_list}\n')
        

        return follower_list
    
    except Exception as err:
        error = f'[Twitch Request] Error in get_follower: {err}'
        log.log_error(error)

# Get a list of Clips from the Twitch Channel
def get_clips():
    try:
        access_token = oauth.Oauth().get_last_tokens()

        last_page = False
        clips_list = []

        url = f'{base_url}/clips'
        HEADERS = {
            'Client-Id': CLIENT_ID,
            'Authorization': f'Bearer {access_token}'
        }
        params = {
            'broadcaster_id': f'{CHANNEL_ID}',
            'first': 100
        }

        while last_page == False:

            response = requests.get(url, headers=HEADERS, params=params)
            response_data = response.json()
            #better_print.try_print(f'\nresponse data: {response_data}\n')
            #better_print.try_print(f'response code: {response.status_code}')

            clips = response_data['data']
            clips_list.append(clips)

            try:
                pagination = response_data['pagination']
                #better_print.try_print(f'Pagination: {pagination}\n')
            except:
                pagination = {}

            try:
                cursor = pagination['cursor']
                #better_print.try_print(f'Cursor: {cursor}\n')
            except:
                pass

            if pagination != {}:
                last_page = False
                params = {
                    'broadcaster_id': f'{CHANNEL_ID}',
                    'first': 100,
                    'after': cursor
                }
            else:
                last_page = True

        return clips_list

    except Exception as err:
        error = f'[Twitch Request] Error in get_clips: {err}'
        log.log_error(error)

# Get a list of Usernames from People that Subscribed the Twitch Channel
def get_broadcaster_supcriptions():
    access_token = oauth.Oauth().get_last_tokens()

    try:
        last_page = False
        subscriber_list = []

        url = f'{base_url}/subscriptions?broadcaster_id={CHANNEL_ID}'
        HEADERS = {
            'Client-Id': CLIENT_ID,
            'Authorization': f'Bearer {access_token}'
        }
        params = {
            'first': 100
        }

        while last_page == False:

            response = requests.get(url, headers=HEADERS, params=params)
            response_data = response.json()

            try:
                pagination = response_data['pagination']
            except:
                pagination = {}
                
            try:
                cursor = pagination['cursor']
                #better_print.try_print(f'Cursor: {cursor}\n')
            except:
                pass

            if pagination != {}:
                last_page = False
                params = {
                    'first': 100,
                    'after': cursor
                }
            else:
                last_page = True


            for username in response_data['data']:
                viewer = str(username['user_name']).lower()
                subscriber_list.append(viewer)

        return subscriber_list
    
    except Exception as err:
        error = f'[Twitch Request] Error in get_broadcaster_supcriptions: {err}'
        log.log_error(error)


# Get a list of usernames from People that have the vip status on the Twitch Channel
def get_vips():
    access_token = oauth.Oauth().get_last_tokens()

    try:
        last_page = False
        vip_list = []

        url = f'{base_url}/channels/vips?broadcaster_id={CHANNEL_ID}'
        HEADERS = {
            'Client-Id': CLIENT_ID,
            'Authorization': f'Bearer {access_token}'
        }
        params = {
            'first': 100
        }

        while last_page == False:

            response = requests.get(url, headers=HEADERS, params=params)
            response_data = response.json()
            #better_print.try_print(f'\nget vip response data: {response_data}\n')

            try:
                pagination = response_data['pagination']
            except:
                pagination = {}
                
            try:
                cursor = pagination['cursor']
                #better_print.try_print(f'Cursor: {cursor}\n')
            except:
                pass

            if pagination != {}:
                last_page = False
                params = {
                    'first': 100,
                    'after': cursor
                }
            else:
                last_page = True

            for username in response_data['data']:
                viewer = str(username['user_name']).lower()
                vip_list.append(viewer)

        return vip_list

    except Exception as err:
        error = f'[Twitch Request] Error in get_vips: {err}'
        log.log_error(error)


# Get the time how long the Person is watching
def followage(viewer, user):
    try:
        #better_print.try_print(viewer, user)
        streamer_id = fetch_user_id(CHANNEL_NAME)
        user_id = fetch_user_id(user)
        #better_print.try_print(f'User ID: {user_id}\n')

        access_token = oauth.Oauth().get_last_tokens()

        url = f'{base_url}/channels/followers?broadcaster_id={streamer_id}&user_id={user_id}'
        HEADERS = {
                    'Client-Id': CLIENT_ID,
                    'Authorization': f'Bearer {access_token}'
                }
        response = requests.get(url,headers=HEADERS)
        response_data = response.json()
        #better_print.try_print(response_data)

        if 'data' in response_data and response_data['data']:
            followed_at = response_data['data'][0]['followed_at']
            followed_date = datetime.fromisoformat(followed_at[:-1])
            current_date = datetime.utcnow()

            duration = current_date - followed_date
            years = duration.days // 365
            months = (duration.days % 365) // 30
            days = (duration.days % 365) % 30

            if viewer == user:
                followed_at = f'@{viewer}, du folgst seit {years} Jahren, {months} Monaten und {days} Tagen. PogChamp'
            else:
                followed_at = f'@{viewer}, @{user} folgt seit {years} Jahren, {months} Monaten und {days} Tagen. PogChamp'
            #better_print.try_print(f'@{viewer} folgt seit {followed_date}!')
        else:
            if user == CHANNEL_NAME.lower():
                followed_at = f'@{viewer}, bro @{user} ist der Channel Creator DarkMode'
                #better_print.try_print(f'@{viewer}, bro @{user} ist der Channel Creator DarkMode')
            else: 
                followed_at = f'@{viewer}, @{user} folgt hier nicht... louisd15Sad'
                #better_print.try_print(f'@{viewer} folgt hier nicht... louisd15sad')
        return followed_at
    except Exception as err:
        error = f'[Twitch Request] Error in followage: {err}'
        log.log_error(error)


# Get the Twitch Game id from the Game
def get_games(game_name):
    try:
        access_token = oauth.Oauth().get_last_tokens()

        url = f'https://api.twitch.tv/helix/games?name={game_name}'
        HEADERS = {
                        'Client-Id': CLIENT_ID,
                        'Authorization': f'Bearer {access_token}'
                }
        response = requests.get(url, headers=HEADERS)
        response_data = response.json()
        game_id = response_data['data'][0]['id']
        is_game = True

        log.log_info(f'[Twitch Request] | info | get_games game_id: {game_id}, is_game: {True}')
        return game_id, is_game
    except Exception as err:
        error = f'[Twitch Request] Error in get_games: {err}'
        log.log_error(error)
        is_game = False
        return '', is_game


# Changed the title from the Twitch Channel
def change_title(title):
    try:
        access_token = oauth.Oauth().get_last_tokens()

    except Exception as err:
        log.logger.info(err)
    try:
        url = f'https://api.twitch.tv/helix/channels?broadcaster_id={CHANNEL_ID}'
        HEADERS = {
                    'Client-Id': CLIENT_ID,
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
        params = {
                    'title': f'{title}'
                }
        response = requests.patch(url, headers=HEADERS, params=params)
        log.logger.info(response.status_code)
        if response.status_code == 204:
            return f'Der Titel wurde zu [{title}] gewechselt.'
        else:
            return f'Etwas ist schief gelaufen NotLikeThis'
    except Exception as err:
        error = f'[Twitch Request] Error in change_title: {err}'
        log.log_error(error)


# Changed the game of from the Twitch Channel
def change_game(game_name):
    try:
        access_token = oauth.Oauth().get_last_tokens()

    except Exception as err:
        log.logger.info(err)
    game_id, _ = get_games(game_name)
    try:
        url = f'https://api.twitch.tv/helix/channels?broadcaster_id={CHANNEL_ID}'
        HEADERS = {
                    'Client-Id': CLIENT_ID,
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
        params = {
                    'game_id': f'{game_id}'
                }
        response = requests.patch(url, headers=HEADERS, params=params)
        #better_print.try_print(response)
        log.logger.info(response.status_code)
        print(response.status_code)
        if response.status_code == 204:
            return f'Spiel wurde zu [{game_name}] gewechselt.'
        elif response.status_code == 400:
            return f'Das Spiel existiert nicht NotLikeThis'
        else:
            return f'Etwas ist schief gelaufen NotLikeThis'
    except Exception as err:
        error = f'[Twitch Request] Error in change_game: {err}'
        log.log_error(error)


# Banning users from Twitch Chat (Permanent or Timeout)
def ban_user(username: str, duration: int, reason: str):
    try:
        access_token = oauth.Oauth().get_last_tokens()

        user_id = int(fetch_user_id(username))

        url = f'{base_url}/moderation/bans'
        HEADERS = {
            'Authorization': f'Bearer {access_token}',
            'Client-Id': CLIENT_ID,
            'Content-Type': 'application/json'
        }
        params = {
            'broadcaster_id': f'{CHANNEL_ID}',
            'moderator_id': f'{CHANNEL_ID}',
        }
        if duration != None:
            data = [{
                'user_id': f'{user_id}',
                'duration': f'{duration}',
                'reason': f'{reason}'
            }]
        else:
            data = [{
                'user_id': f'{user_id}',
                'reason': f'{reason}'
            }]

        request = requests.post(url=url, headers=HEADERS, params=params, data=data)

        if request.status_code == 200:
            return f'@{username} hat sich selbst in den timeout geschickt. louisd15Fine'
        else:
            log.log_info(f'ban user response code: {request.status_code}')
            return None

    except Exception as err:
        error = f'[Twitch Request] Error in ban_user: {err}'
        log.log_error(error)





# needs to be done
def create_custom_rewards(title, cost, prompt):
    access_token = oauth.Oauth().get_last_tokens()

    url = f'{base_url}/channel_points/custom_rewards?broadcaster_id={CHANNEL_ID}'

    HEADERS = {
        'Authorization': f'Bearer {access_token}',
        'Client-Id': CLIENT_ID,
        'Content-Type': 'application/json'
    }

    params = {
        'title': f'{title}',
        'cost': cost,
        'prompt': prompt
    }

    response = requests.post(url, headers=HEADERS, params=params)
    log.log_info(response)

    return


# needs to be done
def get_custom_rewards():
    access_token = oauth.Oauth().get_last_tokens()

    reward_dict = {}

    url = f'{base_url}/channel_points/custom_rewards?broadcaster_id={CHANNEL_ID}'
    
    HEADERS = {
        'Authorization': f'Bearer {access_token}',
        'Client-Id': CLIENT_ID,
        'Content-Type': 'application/json'
    }
    
    params = {
        'only_manageable_rewards': True
    }

    response = requests.get(url, headers=HEADERS, params=params)
    response_data = response.json()
    log.log_info(response_data)

    return

# needs to be done
def update_custom_rewards(reward_id, title, cost):
    access_token = oauth.Oauth().get_last_tokens()

    url = f'{base_url}/channel_points/custom_rewards?broadcaster_id={CHANNEL_ID}&id={reward_id}'

    HEADERS = {
        'Authorization': f'Bearer {access_token}',
        'Client-Id': CLIENT_ID,
        'Content-Type': 'application/json'
    }

    params = {
        'title': f'{title}',
        'cost': cost,
        'is_user_input_required': True
    }

    response = requests.patch(url, headers=HEADERS, params=params)
    response_data = response.json()
    log.log_info(response_data)

    return

# needs to be done
def get_reward_redemption(reward_id):
    try:
        access_token = oauth.Oauth().get_last_tokens()

        reward_id = ''

        url = f'{base_url}/channel_points/custom_rewards/redemptions?broadcaster_id={CHANNEL_ID}&reward_id={reward_id}'

        HEADERS = {
            'Authorization': f'Bearer {access_token}',
            'Client-Id': CLIENT_ID,
            'Content-Type': 'application/json'
        }

        params = {}

        response = requests.get(url, headers=HEADERS, params=params)
        response_data = response.json()
        log.log_info(response_data)

        return
    
    except Exception as err:
        error = f'[Twitch Request] Error in get_reward_redemption: {err}'
        log.log_error(error)





# Updated the redemption status
def update_redemption_status(redemption_id, reward_id, status):
    try:
        access_token = oauth.Oauth().get_last_tokens()

        url = f'{base_url}/channel_points/custom_rewards/redemptions?broadcaster_id={CHANNEL_ID}&reward_id={reward_id}&id={redemption_id}'

        HEADERS = {
            'Authorization': f'Bearer {access_token}',
            'Client-Id': CLIENT_ID,
            'Content-Type': 'application/json'
        }

        if status == 'canceled':
            params = {
                'status': 'CANCELED'
            }

        elif status == 'fulfilled':
            params = {
                'status': 'FULFILLED'
            }

        response = requests.patch(url, headers=HEADERS, params=params)
        #response_data = response.json()
        #log.log_info(response_data)

        return

    except Exception as err:
        error = f'[Twitch Request] Error in update_redemption_status: {err}'
        log.log_error(error)


# needs to be done
def send_whisper(from_user_name, to_user_name, message):
    access_token = oauth.Oauth.get_last_tokens()
    from_user_id = fetch_user_id()
    to_user_id = fetch_user_id()

    url = f'{base_url}/whispers?from_user_id={from_user_id}&to_user_id={to_user_id}'

    HEADERS = {
        'Authorization': f'Bearer {access_token}',
        'Client-Id': CLIENT_ID,
        'Content-Type': 'application/json'
    }

    params = {
        {'message': message}
    }

    response = requests.post(url, headers=HEADERS, params=params)
    response_data = response.json()
    log.log_info(f'Send Whisper respond: {response_data}')

    if response.status_code == 204:
        return True

    return



if __name__ == '__main__':
    oauth.Oauth().validate_token()
