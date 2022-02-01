import os, time, json, re

import spotipy
from spotipy.oauth2     import SpotifyClientCredentials
from discord.message    import Message


import config


# ---------------------------------- JSON ----------------------------------


def load_json(filename, default_return={}):
	try:
		with open(filename, "r") as file:
			return json.load(file)
	except (FileNotFoundError, json.decoder.JSONDecodeError):
		try:
			raise default_return
		except TypeError:
			return default_return



def save_json(filename, data):
	path = os.path.split(filename)[0]

	if not os.path.exists(path):
		os.makedirs(path)

	with open(filename, "w") as file:
		json.dump(data, file, indent=4)


# ---------------------------------- MISC ----------------------------------

def parse_url(txt):
    matched_url = re.search("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", txt)

    if matched_url:
        return matched_url.group(0)


def add_values(d: dict, keys, value):
    """
    Creates nested dictionaries given the provided keys and the value
    """
    intermediate_dict = d
    for i, key in enumerate(keys):
        if type(key) == int:
            key = str(key)

        if i == len(keys) -1:
            intermediate_dict[key] = value
            return

        if key not in intermediate_dict:
            intermediate_dict[key] = {}

        intermediate_dict = intermediate_dict[key]

# --------------------------------- Pycord ---------------------------------

async def standard_reply(message: Message, text, delete_delay = config.delete_delay, **kwargs):
    """
    The standard reply message for this bot, takes additional arguments for the channel.send method
    """
    await message.channel.send(f"{message.author.mention} {text}", delete_after=delete_delay, **kwargs)


# Stores the last time each user was scolder
last_scold_times = {
    # Key: channel id
    # Value: {
        # Key: user id
        # Value: last time this user was scolded
    # }
}


async def scold_user(message: Message, reply_text, delete=True):
    """
    Tell off the user by warning them and deleting the message
    """
    if delete:
        await message.delete()


    channel_id  = message.channel.id
    user_id     = message.author.id


    if channel_id not in last_scold_times:
        last_scold_times[channel_id] = {}
        

    if user_id not in last_scold_times[channel_id]:
        last_scold_times[channel_id][user_id] = time.time()
    
    # skip if the previous message was sent a short time ago
    elif time.time() - last_scold_times[channel_id][user_id] < config.delete_delay + 1:
        return

    else:
        last_scold_times[channel_id][user_id] = time.time()


    await standard_reply(message, reply_text)



sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id       = config.spotify_client_id,
        client_secret   = config.spotify_key
    )
)

def get_spotify_title(song):
    artists = song["artists"]

    title = f"{artists[0]['name']} - {song['name']}"

    if len(artists) > 1:
        extra_artists = [artist["name"] for artist in artists[1:]]

        title += " ft. "
        title += ", ".join(extra_artists)

    return title


def get_api_key(testing=False):
    if testing:
        return os.getenv("DISCORD_API_KEY_TEST")

    return os.getenv("DISCORD_API_KEY")

