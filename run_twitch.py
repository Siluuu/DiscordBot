import threading
from time import sleep
import app.twitch.oauth_2 as oauth

def start_bot():
    thread0 = threading.Thread(target=oauth.setup)

    thread0.start()

    thread0.join()



if __name__ == '__main__':
    oauth.Oauth().validate_token()
    sleep(2)
    start_bot()
