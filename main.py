import time

from discord        import Message
from discord.ext    import commands

from pytube         import YouTube

from misc           import ShareMessageType, get_api_key, get_spotify_title, is_valid_share_message, temporary_reply
import config


previous_message_time = time.time()


bot     = commands.Bot(command_prefix=config.command_prefix)

async def scold_user(message: Message, reply_text, delete=True):
    """
    Tell off the user by warning them and deleting the message
    """
    global previous_message_time

    if delete:
        await message.delete()
    
    # skip if the previous message was sent less than 3 seconds ago
    if time.time() - previous_message_time < config.delete_delay + 1:
        return
    previous_message_time = time.time()

    await temporary_reply(message, reply_text)



async def moderate_share(message: Message):
    """
    moderate the share channel
    """

    is_valid, r = await is_valid_share_message(message)

    if is_valid in {ShareMessageType.YT, ShareMessageType.SPOTIFY}:
        url = r

        title = None

        try:
            if is_valid == ShareMessageType.YT:
                title = YouTube(url).title

            elif is_valid == ShareMessageType.SPOTIFY:
                title = await get_spotify_title(url)

            else:
                await temporary_reply(message, "I currently only support Youtube, Spotify or Attached songs", delete_delay=config.delete_delay + 3)
                return


            if len(title) > 100:
                title = f"{title[:97]}..."

            await message.create_thread(name=title)

        except Exception as e:
            print("Could not find valid song title!")
            print("Message sent:")
            print(message.clean_content)
            print("\n")
            await temporary_reply(message, "Something went wrong getting the song title, you most likely didn't send a valid song!", delete_delay=config.delete_delay + 3)

    elif is_valid == ShareMessageType.FILE:
        attachment = r
        # remove filetype from filename and replace underscores with spaces
        attachment_name = attachment.filename.replace("_", " ")
        thread_title    = ".".join(attachment_name.split(".")[:-1])

        await message.create_thread(name=thread_title)

    elif is_valid in {ShareMessageType.INVALID, ShareMessageType.INVALID_FILE_TYPE, ShareMessageType.INVALID_WEBSITE}:
        text = r
        # if it's an invalid website then we don't delete the message, since it could be an API failure
        delete = is_valid != ShareMessageType.INVALID_WEBSITE

        await scold_user(message, text, delete)



    
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')



@bot.event
async def on_message(message: Message):
    server_id = message.guild.id

    if message.author == bot.user:
        return

    if message.channel.id == config.share_channel_ids[server_id]:
        await moderate_share(message)
        return



# main purpose of this function is to delete thread if the thread's message was deleted
@bot.event
async def on_message_delete(message: Message):
    server_id = message.guild.id

    if message.author == bot.user:
        return
    
    if message.channel.id == config.share_channel_ids[server_id]:
        is_valid, _ = await is_valid_share_message(message)

        # if the message is not a valid share message that means it doesn't have a thread
        if not is_valid.value:
            return

        for thread in message.channel.threads:
            if thread.id == message.id:
                await thread.delete()
                return

        #await moderate_share(message)
        return


bot.run(get_api_key(config.testing))