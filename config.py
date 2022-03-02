# This file takes the different config variables stored in settings and uses them to get additional variables that are often used throughout the system
# This file should not be changed

import os
from os.path    import join, split
from dotenv     import load_dotenv

from settings   import *


# ----------------------------- FOLDERS -----------------------------
file_folder         = split(__file__)[0]

# Folder where private information is stored (API Keys, Playlist IDs, Google client credentials)
secrets_folder      = join(file_folder, "secrets")

# Folder where data is stored ()
data_folder         = join(file_folder, "data")



# ----------------------------- ENV VARS ----------------------------
env_file            = join(secrets_folder, env_filename)
load_dotenv(env_file)


shared_songs_by_songID      = join(data_folder, shared_songs_by_songID_filename)
shared_songs_by_msgID       = join(data_folder, shared_songs_by_msgID_filename)
playlist_items_by_songID    = join(data_folder, playlist_items_by_songID_filename)


# Take Youtube ID and the User credentials depending on if we're testing or not (2 different youtube accounts for testing and normal)

# playlist_channel: channel where the shared songs are updated from
if testing:
    youtube_playlist_id = os.getenv("YT_PLAYLIST_ID_TEST")
    spotify_playlist_id = os.getenv("SP_PLAYLIST_ID_TEST")

    _yt_cred_filename    = "yt channel credentials test"
    playlist_channel     = "927704530903261265"


else:
    youtube_playlist_id = os.getenv("YT_PLAYLIST_ID")
    spotify_playlist_id = os.getenv("SP_PLAYLIST_ID")

    _yt_cred_filename    = "yt channel credentials"
    playlist_channel     = "924352019026833498"


yt_cred_file = join(secrets_folder, _yt_cred_filename)


# ---------------------------- API STUFF ----------------------------
spotify_client_id   = os.getenv("SPOTIFY_API_CLIENT_ID")
spotify_key         = os.getenv("SPOTIFY_API_KEY")