import re, os, spotipy

from enum               import Enum
from urllib.parse       import urlparse


from discord.message    import Message
from spotipy.oauth2     import SpotifyClientCredentials


import config


class ShareMessageType(Enum):
    """
    Enum type for the different types of messages allowed in share type
    """

    # if file type is not video or audio
    INVALID_FILE_TYPE   = -2

    # if website is not youtube or spotify
    INVALID_WEBSITE     = -1

    # if message doesn't contain any songs
    INVALID             = 0

    # if file has successful file
    FILE                = 1
    
    # if url is youtube video
    YT                  = 2
    
    # if url is spotify link
    SPOTIFY             = 3


async def temporary_reply(message: Message, text, delete_delay = config.delete_delay):
    sent_warning = await message.channel.send(f"{message.author.mention} {text}")
    await sent_warning.delete(delay = delete_delay)


async def is_valid_share_message(message: Message):
    """
    check whether a given message is a valid message for the share channel
    """    
    matched_url = re.search("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message.clean_content)

    if matched_url:
        url     = matched_url.group(0).replace("www.", "")
        website = urlparse(url).hostname


        if website in config.youtube_domains:
            msg_type = ShareMessageType.YT

        elif website in config.spotify_domains:
            msg_type = ShareMessageType.SPOTIFY
        
        else:
            url = "Currently the only supported URLs are YouTube and Spotify!"   
            msg_type = ShareMessageType.INVALID_WEBSITE
        

        return msg_type, url


    if len(message.attachments) > 0:
        attachment = message.attachments[0]

        # stop if file is not video or audio
        if attachment.content_type is None or not attachment.content_type.split(";")[0].split("/")[0] in {"audio", "video"}:
            return ShareMessageType.INVALID_FILE_TYPE, "You can only share audio or video files!"

        return ShareMessageType.FILE, attachment

    return ShareMessageType.INVALID, "Discussions are only allowed in the threads!"


async def get_spotify_title(url):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id       = config.spotify_client_id,
        client_secret   = config.spotify_key
    ))

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

