from urllib.parse   import urlparse
from typing         import Set
from pytube         import YouTube

from discord        import Message, Attachment, NotFound, TextChannel


from misc           import add_values, load_json, parse_url, save_json, scold_user, get_spotify_title, standard_reply, scold_user, sp
from misc           import rem_from_playlist, yt_add_to_playlist, sp_add_to_playlist, fetch_songs_from_playlists
from enums          import MessageType, WebsiteType
import config




class ShareMessage:
    """
    Any message in a share channel
    """
    message_type:   MessageType     = MessageType.Normal
    delete:         bool            = False





website_domains = {
    "youtu.be"          : WebsiteType.YouTube,
    "youtube.com"       : WebsiteType.YouTube,

    "open.spotify.com"  : WebsiteType.Spotify,
    "spotify.com"       : WebsiteType.Spotify,
}


def get_website_type(url):
    hostname = urlparse(url.replace("www.", "")).hostname

    if hostname in website_domains:
        return website_domains[hostname]

    return WebsiteType.Other



class ShareURL(ShareMessage):
    """
    A share message that has a url
    """
    url:        str
    website:    WebsiteType


    def __init__(self, url: str, allowed_websites = {*WebsiteType}) -> None:
        self.message_type   = MessageType.Url
        self.url            = url.replace("www.", "")

        website = get_website_type(self.url)


        if website is not None and website in allowed_websites:
            self.website    = website
            return

        self.message_type = MessageType.InvalidUrl



class ShareAttachment(ShareMessage):
    attachment: Attachment


    def __init__(self, attachment: Attachment, allowed_files) -> None:
        self.message_type   = MessageType.File
        self.attachment     = attachment

        if attachment.content_type is None or not attachment.content_type.split(";")[0].split("/")[0] in allowed_files:
            self.message_type = MessageType.InvalidFile




class ThreadChannel:
    """
    A channel where the bot is supposed to creates a thread for each allowed message

    Thread Messages: All
    Banned Messages: None
    """
    # Message types where we create threads
    thread_messages:    Set[MessageType]    = {*MessageType}

    # Message types that are banned in that channel and have to be removed
    banned_messages:    Set[MessageType]    = {}

    # urls that are allowed
    allowed_websites:   Set[WebsiteType]    = {*WebsiteType}

    # files that are allowed
    allowed_files:      Set[str]            = {"audio", "video"}


    # Whether banned messages should get all the elements not in thread_messages
    banned_msgs_opposite: bool              = False

    



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
            MessageType.InvalidFile : "Only audio and video files are allowed!",
            MessageType.InvalidUrl      : f"This url is either not valid or from an unsupported website: {', '.join([site.name for site in self.allowed_websites])}!",
        }

        if self.banned_msgs_opposite:
            self.banned_messages = {*MessageType} - self.thread_messages


    def message_type(self, message: Message):
        url = parse_url(message.clean_content)

        if url:
            return ShareURL(url, self.allowed_websites)


        if len(message.attachments) != 0:
            return ShareAttachment(message.attachments[0], self.allowed_files)

        
        return ShareMessage()


    async def moderate_channel(self, message: Message):
        """
        moderate the share channel, meaning either create a thread or delete a message when necessary
        """
        share_msg = self.message_type(message)

        if share_msg.message_type in self.banned_messages:
            await scold_user(message, f"Cannot send {share_msg.message_type.name} messages in this channel", True)
            return


        # If the message type is not supposed to create a thread, we skip
        if share_msg.message_type not in self.thread_messages:
            return


        thread_title   = None
        if share_msg.message_type.value < 0:
            # Only delete messages that are in the banned messages
            delete_msg = share_msg.message_type in self.banned_messages

            await scold_user(message, self.invalid_messages[share_msg.message_type], delete_msg)
            return


        if share_msg.message_type == MessageType.Url:
            url     = share_msg.url

            website = share_msg.website

            try:
                if website == WebsiteType.YouTube:
                    yt_song         = YouTube(url)

                    thread_title    = yt_song.title
                    song_id         = yt_song.video_id


                elif website == WebsiteType.Spotify:
                    sp_song         = sp.track(url)

                    song_id         = sp_song["id"]
                    thread_title    = get_spotify_title(sp_song)

                
                channel_id  = str(message.channel.id)
                msg_id      = str(message.id)

                shared_songs_by_songID = load_json(config.shared_songs_by_songID)
                shared_songs_by_msgID  = load_json(config.shared_songs_by_msgID)

                # Check whether the song has already been shared
                try:
                    prev_message_ids = shared_songs_by_songID[channel_id][song_id]

                    prev_message: Message = await message.channel.fetch_message(prev_message_ids[0])
                    text = f"The song '{thread_title}' was already shared here before by {prev_message.author.display_name} (See replied message)"

                    await standard_reply(message, text, delete_delay=None, reference=prev_message, mention_author=False)


                # The song has not yet been shared yet
                except KeyError:
                    
                    # Add to playlist
                    playlist_items_by_songID = load_json(config.playlist_items_by_songID)


                    try:
                        if song_id not in playlist_items_by_songID[channel_id]:

                            if website == WebsiteType.YouTube:
                                playlistItemID = yt_add_to_playlist(song_id)["id"]


                            elif website == WebsiteType.Spotify:
                                sp_add_to_playlist(song_id)
                                playlistItemID = song_id


                            add_values(playlist_items_by_songID, [channel_id, song_id], [website.value, playlistItemID])

                            save_json(config.playlist_items_by_songID, playlist_items_by_songID)

                    except:
                        text = f"Was unable to add this song to the {website.name} playlist: {song_id}"

                        print(text)
                        await standard_reply(message, text, delete_delay=config.delete_delay, mention_author=True)


                except NotFound:
                    # When this is raised, it means that the local save of all the shared songs still has this entry, the message was however deleted
                    # In this case we should remove the entry from the local shared songs
                    ...


                # We still have to add the message ID to the list of shared songs since we don't actually delete the message, we leave that up to the user to do
                add_values(shared_songs_by_songID, [channel_id, song_id], [msg_id])
                add_values(shared_songs_by_msgID, [channel_id, msg_id], song_id)

                save_json(config.shared_songs_by_songID, shared_songs_by_songID)
                save_json(config.shared_songs_by_msgID, shared_songs_by_msgID)


            except Exception as e:
                print()
                print("Could not find valid song title!")
                print("Message received from user:")
                print(message.clean_content)
                print()

                reply = f"Something went wrong getting the song title from {website.value}. \nYou most likely didn't send a valid song!"
                await standard_reply(message, reply, delete_delay=config.delete_delay + 2)
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
    banned_messages     = {MessageType.Normal, MessageType.InvalidFile}



class ShareSuggestion(ThreadChannel):
    """
    Channel where you share ideas
    Thread Messages: Normal
    """

    thread_messages     = {MessageType.Normal}

    banned_msgs_opposite = True


class SharePics(ThreadChannel):
    thread_messages     = {MessageType.File, MessageType.Url}

    allowed_files       = {"image", "video"}
    allowed_websites    = {WebsiteType.YouTube}

    banned_msgs_opposite = True





async def sync_messages(channel: TextChannel):
    channel_id = str(channel.id)
    
    # --------------------------- SYNC MESSAGES ---------------------------
    # This part of the code goes through all messages in the channel and adds the songs to the local database here as well as the playlists (currently only youtube)

    shared_songs_by_songID      = load_json(config.shared_songs_by_songID)
    shared_songs_by_msgID       = load_json(config.shared_songs_by_msgID)
    playlist_items_by_songID    = load_json(config.playlist_items_by_songID)

    # Keep all entries except the ones from the channel we're updating
    for d in [shared_songs_by_songID, shared_songs_by_msgID, playlist_items_by_songID]:
        d[channel_id] = {}


    # All the songs that are in the different playlists (YouTube, Spotify)
    playlist_songs = fetch_songs_from_playlists()


    messages = await channel.history(limit=config.nr_messages).flatten()

    print()
    print(f"Found {len(messages)}/{config.nr_messages} messages in '{channel.name}'")
    print()


    for message in messages:
        message: Message
        msg_id = str(message.id)


        # --------------- SYNC LOCAL DATABASE TO MESSAGE ---------------
        url = parse_url(message.clean_content)

        if url is None:
            print(f"Message does not contain url: '{message.clean_content}'")
            continue

        share_msg   = ShareURL(url)
        website     = share_msg.website

        if msg_id not in shared_songs_by_msgID[channel_id]:
            if share_msg.message_type == MessageType.InvalidUrl:
                print(f"Could not ID the following url: '{share_msg.url}'")
                continue


            # Get song ID and add the song to the local databases

            if website == WebsiteType.YouTube:
                song_id = YouTube(url).video_id


            elif website == WebsiteType.Spotify:
                song_id = sp.track(url)["id"]


            else:
                print("Invalid website! Can't get necessary ID!")
                continue


            add_values(shared_songs_by_songID, [channel_id, song_id], [msg_id])
            add_values(shared_songs_by_msgID, [channel_id, msg_id], song_id)

        else:
            song_id = shared_songs_by_msgID[channel_id][msg_id]
            print("This message is already in the 'shared_songs_by_msgID.json' database!")


        # --------------- SYNC REMOVE PLAYLIST TO MESSAGE ---------------
        if song_id not in playlist_items_by_songID or song_id not in playlist_songs:

            # If the song is already in a playlist we fetch the playlistItemID here
            if song_id in playlist_songs:
                playlistItemID = playlist_songs[song_id][1]
            

            # If it isn't we add it
            else:
                if website == WebsiteType.YouTube:
                    playlistItemID = yt_add_to_playlist(song_id)["id"]
                
                elif website == WebsiteType.Spotify:
                    sp_add_to_playlist(song_id)
                    playlistItemID = song_id


                else:
                    print("Can't add song to playlist from this website!")
                    continue


                playlist_songs[song_id]         = [website.value, playlistItemID]

            add_values(playlist_items_by_songID, [channel_id, song_id], [website.value, playlistItemID])

        else:
            print("Song Already in Playlist!")



    save_json(config.shared_songs_by_songID, shared_songs_by_songID)
    save_json(config.shared_songs_by_msgID, shared_songs_by_msgID)
    save_json(config.playlist_items_by_songID, playlist_items_by_songID)



    # --------------------------- REMOVE EXCESS SONGS FROM PLAYLIST ---------------------------
    # This part of the code goes through all songs in a playlist and makes sure those songs are still posted at least once in the channel
    # If there is no message with the song, the song is removed from the playlist

    for videoID, (website, playlistItemID) in playlist_songs.items():
        if not videoID in playlist_items_by_songID[channel_id]:
            rem_from_playlist(playlistItemID, website=website)



# Key:      discord server ID
# Value:    list of channels
thread_channels_per_server = {
    # Main discord server
    924350783892389939 : [
        ShareMedia(924352019026833498),
        SharePics(933058673872367737),
        SharePics(932736792443092992),
        ShareSuggestion(927726978948296715),
        ThreadChannel(935922814869987388)
    ],

    # Test discord server
    927704499194310717 : [
        ShareMedia(927704530903261265,      test_server=True),
        ShareSuggestion(937080002674040952, test_server=True),
        SharePics(937500000391413880,       test_server=True),
    ]
}