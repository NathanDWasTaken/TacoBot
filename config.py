import os
from dotenv import load_dotenv


# Load api_key.env
file_folder = os.path.split(__file__)[0]
env_file    = os.path.join(file_folder, "api_key.env")
load_dotenv(env_file)




testing         = True
test_server_id  = 927704499194310717


command_prefix  = "$"
delete_delay    = 5


data_folder         = os.path.join(file_folder, "data")
shared_songs_file   = os.path.join(data_folder, "shared_songs.json")



# ---------------------------- API STUFF ----------------------------
spotify_client_id   = os.getenv("SPOTIFY_API_CLIENT_ID")
spotify_key         = os.getenv("SPOTIFY_API_KEY")