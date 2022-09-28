# This file holds all of the config variables
# Params here can be changed


testing                 = False


env_filename            = "secrets.env"

spotify_cache_filename  = "SpotipyOAuth.cache"

# Stores the shared songs where the last key is the song ID
shared_songs_by_songID_filename    = "shared_songs_by_songID.json"

# Stores the shared songs where the last key is the discord message ID
shared_songs_by_msgID_filename     = "shared_songs_by_msgID.json"

# Stores all the songs that have been added to a playlist. 
playlist_items_by_songID_filename  = "playlist_items_by_songID.json"


# ID of the test discord server
test_server_id          = 927704499194310717


command_prefix          = "$"
delete_delay            = 5

# Number of messages the bot will fetch from a channel
nr_messages             = 1000

spotify_scopes          = ["playlist-modify-private", "playlist-modify-public", "playlist-read-private"]

# Number of tracks we want to receive for each request to spotify api
spotify_request_size    = 100