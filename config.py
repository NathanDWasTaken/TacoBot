import os
from dotenv import load_dotenv

file_folder = os.path.split(__file__)[0]
env_file    = os.path.join(file_folder, "api_key.env")
load_dotenv(env_file)



testing = True

# Key:      discord server ID
# Value:    share-music channel ID
share_channel_ids = {
    924350783892389939 : 924352019026833498,
    927704499194310717 : 927704530903261265
}


command_prefix  = "$"
delete_delay    = 3



# ---------------------------- API STUFF ----------------------------
youtube_domains = {
    "youtu.be",
    "youtube.com"
    }

spotify_domains = {
    "open.spotify.com",
    "spotify.com"
}


spotify_client_id   = os.getenv("SPOTIFY_API_CLIENT_ID")
spotify_key         = os.getenv("SPOTIFY_API_KEY")