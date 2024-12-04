import os
import requests
import asyncio
import json
from dotenv import load_dotenv
import app.logging as log

load_dotenv()

# oauth class
class Oauth():
    def __init__(self):
        self.filename = 'json/twitch/oauth.json'
        self.client_id = os.getenv('TWITCH_CLIENT_ID')
        self.client_secret = os.getenv('TWITCH_CLIENT_SECRET')
        self.oauth_json = {}
        self.access_token = os.getenv('TWITCH_ACCESS_TOKEN')
        self.refresh_token  = os.getenv('TWITCH_REFRESH_TOKEN')
        self.expires_in = 0
        self.get_last_tokens()


    # get the latest access token from the oauth.json
    def get_last_tokens(self):
        try:
            with open(self.filename, 'r') as load_file:
                self.oauth_json = json.load(load_file)
                self.access_token = self.oauth_json['ACCESS_TOKEN']
                self.refresh_token = self.oauth_json['REFRESH_TOKEN']

            if self.access_token == '' or self.refresh_token == '':
                self.access_token = os.getenv('TWITCH_ACCESS_TOKEN')
                self.refresh_token = os.getenv('TWITCH_REFRESH_TOKEN')

            return self.access_token
        
        except Exception as err:
            error = f'[Twitch Oauth] Error in get_last_access_token: {err}'
            log.log_error(error)

    
    # saves the new access and refresh token to the oauth.json
    def save_new_tokens(self):
        try:
            self.oauth_json['ACCESS_TOKEN'] = self.access_token
            self.oauth_json['REFRESH_TOKEN'] = self.refresh_token

            with open(self.filename, 'w') as load_file:
                json.dump(self.oauth_json, load_file, indent=4)

            return

        except Exception as err:
            error = f'[Twitch Oauth] Error in save_new_token: {err}'
            log.log_error(error)


    # validate the access token
    def validate_token(self):
        try:
            url = 'https://id.twitch.tv/oauth2/validate'

            HEADERS = {
                'Authorization': f'Bearer {self.access_token}',
            }

            response = requests.get(url, headers=HEADERS)
            response_data = response.json()

            status_code = response.status_code

            if status_code == 401:
                self.refresh_access_token()
                
            elif status_code == 200:
                self.expires_in = int(response_data['expires_in'])
                return True

        except Exception as err:
            error = f'[Twitch Oauth] Error in validate_token: {err}'
            log.log_error(error)


    # refreshes the access token
    def refresh_access_token(self):
        try:
            url = 'https://id.twitch.tv/oauth2/token'

            HEADERS = {
                'Content_Type': 'application/x-www-form-urencoded'
            }

            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }

            response = requests.post(url, data, headers=HEADERS)
            response_data = response.json()
            status_code = response.status_code

            if status_code == 400:
                #Invalid refresh token
                return
            elif status_code == 401:
                #New connection to Twitch needed
                return

            self.access_token = response_data['access_token']
            self.refresh_token = response_data['refresh_token']
            
            self.validate_token()
            self.save_new_tokens()

            return

        except Exception as err:
            error = f'[Twitch Oauth] Error in validate_token: {err}'
            log.log_error(error)


    # checks if the access token is still valid
    async def check_validation(self):
        try:
            while True:
                if self.expires_in <= 0:
                    self.validate_token()

                elif self.expires_in != 0:
                    self.expires_in = self.expires_in - 600

                    if self.expires_in <= 720:
                        self.refresh_access_token()

                await asyncio.sleep(600)
        
        except Exception as err:
            error = f'[Twitch Oauth] Error in check_validation: {err}'
            log.log_error(error)













def setup():
    oauth_system = Oauth()
    asyncio.run(oauth_system.check_validation())


if __name__ == '__main__':
    setup()