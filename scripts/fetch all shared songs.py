# Goes over all messages in the given channel and adds all the spotify and youtube songs to the local json files (which is used to keep track of what songs have already been posted)


# Allows us to import files from parent dir
import os, sys

dir = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(dir)

sys.path.append(parent_folder)
# https://stackoverflow.com/questions/16780014/import-file-from-parent-directory


import config
from misc           import get_api_key, parse_url, load_json, save_json, add_values, sp
from classes        import MessageType, ShareURL, WebsiteType


from discord        import Message
from discord.ext    import commands
from pytube         import YouTube


bot     = commands.Bot()


if config.testing:
    channel_id = 927704530903261265
else:
    channel_id = 924352019026833498

nr_messages = 300


    
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


    shared_songs_by_songID  = load_json(config.shared_songs_by_songID)
    shared_songs_by_msgID   = load_json(config.shared_songs_by_msgID)

    share_edm = bot.get_channel(channel_id)
    messages = await share_edm.history(limit=nr_messages).flatten()

    print("\n")
    print(f"Found {len(messages)}/{nr_messages} messages in '{share_edm.name}'")
    print("\n")

    for message in messages:
        message: Message
        url = parse_url(message.clean_content)

        if url is None:
            print(f"Message does not contain url: '{message.clean_content}'")
            continue

        share_msg = ShareURL(url)

        if share_msg.message_type == MessageType.InvalidUrl:
            print(f"Could not ID the following url: '{share_msg.url}'")
            continue

        website = share_msg.website

        if website == WebsiteType.YouTube:
            song_id = YouTube(url).video_id

        elif website == WebsiteType.Spotify:
            song_id = sp.track(url)["id"]


        msg_id = str(message.id)

        add_values(shared_songs_by_songID, [message.channel.id, song_id], [msg_id])
        add_values(shared_songs_by_msgID, [msg_id], song_id)


    save_json(config.shared_songs_by_songID, shared_songs_by_songID)
    save_json(config.shared_songs_by_msgID, shared_songs_by_msgID)

    bot.loop.stop()
    




bot.run(get_api_key(config.testing))