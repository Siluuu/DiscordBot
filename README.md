# DiscordBot

## Overview

This is a Discord Bot designed to enhance interaction and engagement between Twitch streamers and their communities. The bot is built to streamline live activity notifications, role assignments based on Twitch interactions, and other automated tasks, all integrated with Discord's slash commands.

## Features

- **Live Status Tracking**:

  - Updates the bot's activity to show when a specified user is live on Twitch.
  - Displays an "Edging streak" counter for idle activity, incrementing daily.

- **Role Management**:

  - Automatically assigns roles based on Twitch subscriptions or channel point redemptions.
  - Provides moderators with easy role control through slash commands.

- **Twitch Clip Automation**:

  - Monitors Twitch for newly created clips and posts them in a designated Discord channel with details:
    ```
    Clip created by [username]
    [clip title]
    [clip link]
    ```

- **Slash Commands**:

  - A comprehensive set of commands for users and moderators:
    - `/say [text] [channel]`: Send messages as the bot (mods only).
    - `/profile [user]`: View user details, such as account creation and join dates.
    - `/games`: Display the list / queue of games requested by viewers for the streams.
    - `/removegame [number]`: Remove a game from the queue (mods only).
    - `/submit [link]`: Submit a video for the ylyl streams.
    - `/blacklist [link]`: Add a video to the blacklist for ylyl submission (mods only).
    - `/stats`: Summarize Twitch stats (mods only).
    - `/cleardms [number]`: Deletes the bot's messages in DMs.

- **Community Interaction**:

  - Handles video submissions and moderates content using reactions.
  - Welcomes new members with an automated message.

- **Utility Tools**:

  - Fetches detailed Twitch stats, including followers, mods, VIPs and subscribers.
  - Provides debug utilities for testing bot functionality.

## File Structure

```
TwitchBot
├── app
│   ├── discord
│   │   ├── cogs
│   │   │   ├── activity_management.py
│   │   │   ├── clip_management.py
│   │   │   ├── role_management.py
│   │   │   ├── slash_commands.py
│   │   ├── __init__.py
│   │   ├── discord_bot.py
│   ├── style
│   │   ├── __init__.py
│   │   ├── better_print.py 
│   ├── twitch
│   │   ├── __init__.py
│   │   ├── request.py 
│   ├── __init__.py
│   ├── logging.py
├── json
│   ├── discord
│   │   ├── request_verification.json
│   │   ├── video_blacklist.json
│   │   ├── video_submittedlist.json
│   │   ├── verifyed_users.json
├── .env
├── README.md
├── requirements.txt
├── run_discord.py
├── start.bat
└── start.sh
```

## Note

Before you start the bot, replace the placeholder in the `.env` file.

##

### For Windows user

You need to execute `start.bat`

### For the Linux user

 You have to do a few steps:

- **First**
You need to install `dos2unix`:
```
sudo apt install dos2unix -y
```

- **Second**
Go to the directory of the bot and do as follow:
```
dos2unix start.sh
```

- **Third**
Give the `start.sh` execute permission:
```
chmod +x start.sh
```

- **Last**
You can start the bot with:
```
./start.sh
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer
By using this project, you agree to comply with the licenses of all third-party dependencies. Additionally, if you use this bot to interact with services like Twitch, you must ensure compliance with their terms of service and developer policies.
