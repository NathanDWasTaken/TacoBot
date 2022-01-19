# TacoBot
This repository is the code used for my small discord bot for a private discord server.

The main purpose of the bot is to manage share-music channels. As the name implies, the goal of the channel is to share music in them. The bot's job is to remove any messages that do not contain any music (either url to a song or a file). If the message is a song, then the bot will automatically create a discord thread for it, so people can discuss or give feedback about the song there.

## How to run
In order to successfully run the code, you first of all need the following libraries:
- dotenv
- pycord
- spotipy
- pytube

Watch out with pycord in particular, because when I installed it via pip the version was older and didn't support threads yet, so I had to download the latest version from [their github page](https://github.com/Pycord-Development/pycord):

What we need is the discord folder in that repository, the easiest way to get it is by clicking the green "Code" dropdown menu and downloading the zip. Once that zip is downloaded, open it and copy the entire discord folder to your python install directory in Lib/site-packages. There might already be a discord folder because you installed it, simply replace it.


Another thing you will need is API keys, one for discord and one for spotify.

You'll have to create your own bot as well as discord test server in order to successfully run it. The server's ID the share-channel's ID (the one that should be moderated) should be added to the config.py/share_channel_ids dict as a key-value pair. 

Next you need to create a `api_key.env` file with the following variables:
```
# Having 2 seperate bots, one that is used and another for testing is helpful because it allows us to work on the bot while the actual bot is still online.
DISCORD_API_KEY         = "your-api-key"            # The discord bot's api key, is used when testing is set tp False in config.py
DISCORD_API_KEY_TEST    = "your-test-pi-key"        # The test bot's api key, is used when testing is set to True in config.py

SPOTIFY_API_CLIENT_ID   = "your-spotify-client-id"  # Spotify app client ID
SPOTIFY_API_KEY         = "your-spotify-api-key"    # Spotify appclient secret
```
