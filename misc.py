import os, spotipy, time


from discord.message    import Message
from spotipy.oauth2     import SpotifyClientCredentials


import config



async def temporary_reply(message: Message, text, delete_delay = config.delete_delay):
    sent_warning = await message.channel.send(f"{message.author.mention} {text}")
    await sent_warning.delete(delay = delete_delay)



previous_message_time = time.time()


async def scold_user(message: Message, reply_text, delete=True):
    """
    Tell off the user by warning them and deleting the message
    """
    global previous_message_time

    if delete:
        await message.delete()
    
    # skip if the previous message was sent a short time ago
    if time.time() - previous_message_time < config.delete_delay + 1:
        return
    previous_message_time = time.time()

    await temporary_reply(message, reply_text)



sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id       = config.spotify_client_id,
        client_secret   = config.spotify_key
    )
)

def get_spotify_title(url):
    song = sp.track(url)

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

