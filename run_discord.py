import threading
import app.discord.discord_bot as discord_bot

def start_bot():
    thread0 = threading.Thread(target=discord_bot.discord_bot_start)

    thread0.start()
    
    thread0.join()

if __name__ == '__main__':
    start_bot()