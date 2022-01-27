import time

from discord        import Message
from discord.ext    import commands

from pytube         import YouTube

from misc           import MessageType, ValidityType, WebsiteType, get_api_key, get_spotify_title, is_valid_share_message, temporary_reply, invalid_messages
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

    share_msg = await is_valid_share_message(message)


    if share_msg.validity != ValidityType.Valid:
        # Don't delete message if it's a website, maybe it's soundcloud?
        delete_msg = share_msg.validity != ValidityType.InvalidWebsite
        await scold_user(message, invalid_messages[share_msg.validity], delete_msg)
        return



    if share_msg.message_type == MessageType.Url:
        title   = None
        url     = share_msg.url


        try:
            if share_msg.website == WebsiteType.YouTube:
                title = YouTube(url).title

            elif share_msg.website == WebsiteType.Spotify:
                title = await get_spotify_title(url)


            if len(title) > 100:
                title = f"{title[:97]}..."

            await message.create_thread(name=title)


        except Exception as e:
            print("Could not find valid song title!")
            print("Message received from user:")
            print(message.clean_content)
            print("\n")
            await temporary_reply(message, f"Something went wrong getting the song title from {share_msg.website.value}. \nYou most likely didn't send a valid song!", delete_delay=config.delete_delay + 2)


    elif share_msg.message_type == MessageType.File:
        # remove filetype from filename and replace underscores with spaces
        attachment_name = share_msg.attachment.filename.replace("_", " ")
        thread_title    = ".".join(attachment_name.split(".")[:-1])

        await message.create_thread(name=thread_title)




    
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
        share_msg = await is_valid_share_message(message)

        # if the message is not a valid share message that means it doesn't have a thread
        if share_msg.validity != ValidityType.Valid:
            return

        for thread in message.channel.threads:
            if thread.id == message.id:
                await thread.delete()
                return

        #await moderate_share(message)
        return


bot.run(get_api_key(config.testing))