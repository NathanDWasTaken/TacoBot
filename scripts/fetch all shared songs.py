# Allows us to import files from parent dir
import os, sys

dir = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(dir)

sys.path.append(parent_folder)
# https://stackoverflow.com/questions/16780014/import-file-from-parent-directory


import config
from misc           import get_api_key, parse_url, load_json, save_json, add_values, sp
from classes        import ShareURL, WebsiteType


from discord        import Message
from discord.ext    import commands
from pytube         import YouTube


bot     = commands.Bot()


channel_id  = 927704530903261265
nr_messages = 300


    
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


    shared_songs = load_json(config.shared_songs_file, {})

    share_edm = bot.get_channel(channel_id)
    messages = await share_edm.history(limit=nr_messages).flatten()

    print("\n")
    print(f"Found {len(messages)}/{nr_messages} messages in '{share_edm.name}'")
    print("\n")

    for message in messages:
        message: Message
        url = parse_url(message.clean_content)

        share_msg = ShareURL(url)
        website = share_msg.website

        if website == WebsiteType.YouTube:
            song_id = YouTube(url).video_id

        elif website == WebsiteType.Spotify:
            song_id = sp.track(url)["id"]

        
        keys = (message.channel.id, website.name, song_id)

        add_values(shared_songs, keys, message.id)


    save_json(config.shared_songs_file, shared_songs)

    bot.loop.stop()
    




bot.run(get_api_key(config.testing))