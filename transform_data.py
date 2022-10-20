from natlib     import load_json, save_json
from os.path    import join

import config



playlistSongs_by_songID = load_json(config.shared_songs_by_songID)
playlistItems_by_songID = load_json(config.playlist_items_by_songID)


playlistSongs = {}

for serverID, songs in playlistSongs_by_songID.items():
    playlistSongs[serverID] = {}

    for songID, messageIDs in songs.items():
        website_type, playlistItemID = playlistItems_by_songID[serverID][songID]
        playlistSongs[serverID][songID] = [
            messageIDs,
            website_type,
            playlistItemID
        ]



save_json(join(config.data_folder, "playlistSongs.json"), playlistSongs)