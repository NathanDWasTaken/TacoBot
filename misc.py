import re, os, spotipy

from enum               import Enum
from urllib.parse       import urlparse


from discord.message    import Message, Attachment
from spotipy.oauth2     import SpotifyClientCredentials


import config




class MessageType(Enum):
    Url         = 1
    File        = 2


class ValidityType(Enum):
    Valid   = 1

    # Whenever a message is invalid, meaning that it does not belong in the channel
    Invalid = 0

    # Whenever a file is Invalid
    InvalidFileType = -1

    # Whenever a website is not part of the allowed websites
    InvalidWebsite  = -2



class ShareMessage:
    """
    Any message in a share channel
    """
    message_type:     MessageType
    validity        = ValidityType.Valid

    def __init__(self, validity = ValidityType.Invalid) -> None:
        self.validity = validity



class WebsiteType(Enum):
    """
    Enum for all currently supported websites
    """
    YouTube = "youtube"
    Spotify = "spotify"




class ShareURL(ShareMessage):
    """
    A share message that has a url
    """
    url:        str
    website:    WebsiteType

    website_domains = {
        "youtu.be"          : WebsiteType.YouTube,
        "youtube.com"       : WebsiteType.YouTube,

        "open.spotify.com"  : WebsiteType.Spotify,
        "spotify.com"       : WebsiteType.Spotify,
    }


    def __init__(self, url: str) -> None:
        self.message_type   = MessageType.Url
        self.url            = url.replace("www.", "")

        hostname            = urlparse(self.url).hostname

        if hostname in self.website_domains:
            self.website    = self.website_domains[hostname]
        else:
            self.validity = ValidityType.InvalidWebsite



class ShareAttachment(ShareMessage):
    attachment: Attachment


    def __init__(self, attachment: Attachment) -> None:
        self.message_type   = MessageType.File
        self.attachment     = attachment

        if attachment.content_type is None or not attachment.content_type.split(";")[0].split("/")[0] in {"audio", "video"}:
            self.validity = ValidityType.InvalidFileType



invalid_messages = {
    ValidityType.Invalid            : "You can only post songs in the form of a link from a supported website or an audio/video file!",
    ValidityType.InvalidFileType    : "Only audio and video files are allowed!",
    ValidityType.InvalidWebsite     : f"I currently only support the following websites: {', '.join([site.name for site in WebsiteType])}!",
}



async def temporary_reply(message: Message, text, delete_delay = config.delete_delay):
    sent_warning = await message.channel.send(f"{message.author.mention} {text}")
    await sent_warning.delete(delay = delete_delay)


async def is_valid_share_message(message: Message):
    """
    check whether a given message is a valid message for the share channel
    """    
    matched_url = re.search("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message.clean_content)

    if matched_url:
        url     = matched_url.group(0)

        return ShareURL(url)


    if len(message.attachments) != 0:
        return ShareAttachment(message.attachments[0])


    return ShareMessage()


sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id       = config.spotify_client_id,
        client_secret   = config.spotify_key
    )
)

async def get_spotify_title(url):
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

