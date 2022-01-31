import re

from enum               import Enum
from urllib.parse       import urlparse
from typing             import Set
from pytube             import YouTube

from discord.message    import Message, Attachment


from misc               import scold_user, get_spotify_title, temporary_reply, scold_user

import config


class MessageType(Enum):
    """
    The different types of messages there are
    """
    # A message that contains any url
    Url         = 1

    # A message that contains a file
    File        = 2

    # A message that is none of the above
    Normal      = 0



class ValidityType(Enum):
    """
    Enum for the validity of a message
    """
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
    message_type:   MessageType     = MessageType.Normal
    validity:       ValidityType    = ValidityType.Valid



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
    thread_messages:    Set[MessageType] = {*MessageType}

    # Message types that are banned in that channel and have to be removed
    banned_messages:    Set[MessageType] = {}

    # urls that are allowed
    allowed_websites:   Set[WebsiteType] = {*WebsiteType}

    



    def __init__(self, channel_id, test_server=False, thread_msgs=None, banned_msgs=None, allowed_sites=None) -> None:
        self.id = channel_id

        if thread_msgs is not None:
            self.thread_messages    = thread_msgs
        
        if banned_msgs is not None:
            self.banned_messages    = banned_msgs

        if allowed_sites is not None:
            self.allowed_websites   = allowed_sites


        self.test_server        = test_server
        

        # Error messages for the different invalid message types
        self.invalid_messages = {
            ValidityType.Invalid            : "You can only post songs in the form of a link from a supported website or an audio/video file!",
            ValidityType.InvalidFileType    : "Only audio and video files are allowed!",
            ValidityType.InvalidWebsite     : f"Only urls to the following websites are allowed: {', '.join([site.name for site in self.allowed_websites])}!",
        }


    def message_type(self, message: Message):
        matched_url = re.search("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message.clean_content)

        if matched_url:
            url     = matched_url.group(0)

            return ShareURL(url, self.allowed_websites)


        if len(message.attachments) != 0:
            return ShareAttachment(message.attachments[0])

        
        return ShareMessage()


    async def moderate_channel(self, message: Message):
        """
        moderate the share channel, meaning either create a thread or delete a message when necessary
        """
        share_msg = self.message_type(message)

        if share_msg.message_type in self.banned_messages:
            await scold_user(message, f"Cannot send {share_msg.message_type.name} messages in this channel", True)
            return



        if share_msg.message_type not in self.thread_messages:
            return


        thread_title   = None
        if share_msg.validity != ValidityType.Valid:
            # Don't delete message if it's a website, maybe it's soundcloud?
            delete_msg = share_msg.message_type in self.banned_messages

            await scold_user(message, self.invalid_messages[share_msg.validity], delete_msg)
            return


        if share_msg.message_type == MessageType.Url:
            url     = share_msg.url

            website = share_msg.website

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

                reply = f"Something went wrong getting the song title from {website.value}. \nYou most likely didn't send a valid song!"
                await temporary_reply(message, reply, delete_delay=config.delete_delay + 2)
                return



        elif share_msg.message_type == MessageType.File:
            # remove filetype from filename and replace underscores with spaces
            attachment_name = share_msg.attachment.filename.replace("_", " ")
            thread_title    = ".".join(attachment_name.split(".")[:-1])


        elif share_msg.message_type == MessageType.Normal:
            thread_title = message.author.display_name

        
        # Shorten thread title
        if len(thread_title) > 100:
            thread_title = f"{thread_title[:97]}..."

        await message.create_thread(name=thread_title)


        

class ShareMedia(ThreadChannel):
    """
    Channel where you're supposed to share music (only urls to correct sites)
    """

    thread_messages     = {MessageType.Url, MessageType.File}
    banned_messages     = {MessageType.Normal}
    allowed_websites    = {*WebsiteType}



class ShareSuggestion(ThreadChannel):
    """
    Channel where you share ideas
    """

    thread_messages     = {MessageType.Normal}
    banned_messages     = {MessageType.Url, MessageType.File}



# Key:      discord server ID
# Value:    list of channels
thread_channels_per_server = {
    # Main discord server
    924350783892389939 : [
        ShareMedia(924352019026833498)
    ],

    # Test discord server
    927704499194310717 : [
        ShareMedia(927704530903261265, test_server=True),
        ShareSuggestion(937080002674040952, test_server=True)
    ]
}