import os
import shutil
import app.logging as log


def try_print(text):
    try:
        print(text)
    except:
        pass


def print_centered(text):
    # Ermitteln der Bildschirmbreite
    columns, _ = shutil.get_terminal_size()

    # Berechnen der Anzahl an Leerzeichen für die Zentrierung
    padding = (columns - len(text)) // 2

    # Ausgabe des zentrierten Texts
    centerd = " " * padding + text
    log.logger.info(centerd)
    try_print(centerd)


# Clear screen (optional)
os.system('cls' if os.name == 'nt' else 'clear')


def first_print():
    first_print = '╔══════════════════════════════════╗'

    try_print('\n')
    first_print = print_centered(first_print)


def discord_bot_ready(bot_name):
    discord_bot_ready = f'║     {bot_name} is ready!      ║'

    discord_bot_ready = print_centered(discord_bot_ready)


def last_print():
    last_print = '╚══════════════════════════════════╝'

    last_print = print_centered(last_print)
    try_print('\n\n\n')


def test_prints():
    first_print()
    discord_bot_ready()
    last_print()




if __name__ == '__main__':
    test_prints()
