import re

from enum               import Enum
from urllib.parse       import urlparse
from typing             import Set
from pytube             import YouTube

from discord.message    import Message, Attachment


from misc               import scold_user, get_spotify_title, temporary_reply, scold_user

import config


class MessageType(Enum):
    # A message that contains any url
    Url         = 1

    # A message that contains a file
    File        = 2

    # A message that is none of the above
    Normal      = 0



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


    def __init__(self, url: str, allowed_websites = {*WebsiteType}) -> None:
        self.message_type   = MessageType.Url
        self.url            = url.replace("www.", "")

        hostname            = urlparse(self.url).hostname

        if hostname in self.website_domains:
            website = self.website_domains[hostname]

            if website in allowed_websites:
                self.website    = website
                return

        self.validity = ValidityType.InvalidWebsite



class ShareAttachment(ShareMessage):
    attachment: Attachment


    def __init__(self, attachment: Attachment) -> None:
        self.message_type   = MessageType.File
        self.attachment     = attachment

        if attachment.content_type is None or not attachment.content_type.split(";")[0].split("/")[0] in {"audio", "video"}:
            self.validity = ValidityType.InvalidFileType




class ThreadChannel:
    """
    A channel where the bot is supposed to creates a thread for each allowed message
    """
    # Message types where we create threads
    thread_messages:    Set[MessageType]    = {MessageType.Normal, MessageType.Url, MessageType.File}

    # Message types that are banned in that channel and have to be removed
    banned_messages:    Set[MessageType]    = {}

    # urls that are allowed
    allowed_websites:   Set[WebsiteType]    = {}

    
    # Error messages for the different invalid message types
    invalid_messages = {
        ValidityType.Invalid            : "You can only post songs in the form of a link from a supported website or an audio/video file!",
        ValidityType.InvalidFileType    : "Only audio and video files are allowed!",
        ValidityType.InvalidWebsite     : f"I currently only support the following websites: {', '.join([site.name for site in allowed_websites])}!",
    }



    def __init__(self, channel_id) -> None:
        self.id = channel_id
        


    def is_valid(self, message: Message):
        if MessageType.Url not in self.banned_messages:
            matched_url = re.search("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message.clean_content)

            if matched_url:
                url     = matched_url.group(0)

                return ShareURL(url, self.allowed_websites)


        if MessageType.File not in self.banned_messages:
            if len(message.attachments) != 0:
                return ShareAttachment(message.attachments[0])

        
        return ShareMessage()


    async def moderate_channel(self, message: Message):
        """
        moderate the share channel, meaning either create a thread or delete a message when necessary
        """
        share_msg = self.is_valid(message)

        thread_title   = None


        if share_msg.validity != ValidityType.Valid:
            # Don't delete message if it's a website, maybe it's soundcloud?
            delete_msg = share_msg.validity != ValidityType.InvalidWebsite

            await scold_user(message, self.invalid_messages[share_msg.validity], delete_msg)
            return


        elif share_msg.message_type == MessageType.Url:
            url     = share_msg.url

            website = share_msg.website

            if website not in self.allowed_websites:
                await temporary_reply(message, "")


            try:
                if website == WebsiteType.YouTube:
                    thread_title = YouTube(url).title

                elif website == WebsiteType.Spotify:
                    thread_title = get_spotify_title(url)


            except Exception as e:
                print("Could not find valid song title!")
                print("Message received from user:")
                print(message.clean_content)
                print("\n")
                await temporary_reply(message, f"Something went wrong getting the song title from {website.value}. \nYou most likely didn't send a valid song!", delete_delay=config.delete_delay + 2)



        elif share_msg.message_type == MessageType.File:
            # remove filetype from filename and replace underscores with spaces
            attachment_name = share_msg.attachment.filename.replace("_", " ")
            thread_title    = ".".join(attachment_name.split(".")[:-1])

        
        # Shorten thread title
        if len(thread_title) > 100:
            thread_title = f"{thread_title[:97]}..."

        await message.create_thread(name=thread_title)


        

class ShareMedia(ThreadChannel):
    """
    Channel where you're supposed to share music (only urls to correct sites)
    """

    allowed_messages = {MessageType.Url, MessageType.File}

    allowed_websites = {WebsiteType.YouTube, WebsiteType.Spotify}




# Key:      discord server ID
# Value:    list of channels
thread_channels_per_server = {
    # Main discord server
    924350783892389939 : [
        ShareMedia(924352019026833498)
    ],

    # Test discord server
    927704499194310717 : [
        ShareMedia(927704530903261265)
    ]
}