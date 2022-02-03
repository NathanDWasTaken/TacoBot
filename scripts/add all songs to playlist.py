# Currently only supports youtube playlist

# Goal of this is to loop over each message in the given channel and then add it to the youtube playlist (if it's a youtube song)



# Allows us to import files from parent dir
import os, sys

dir = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(dir)

sys.path.append(parent_folder)
# https://stackoverflow.com/questions/16780014/import-file-from-parent-directory


import config
from misc           import get_api_key, parse_url, yt_add_to_playlist
from classes        import MessageType, ShareURL, WebsiteType


from discord        import Message
from discord.ext    import commands
from pytube         import YouTube


bot     = commands.Bot()


channel_id  = 927704530903261265
nr_messages = 300


    
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


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

            yt_add_to_playlist(song_id)

        elif website == WebsiteType.Spotify:
            ...



    bot.loop.stop()

bot.run(get_api_key(config.testing))