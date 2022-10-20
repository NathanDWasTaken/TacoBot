from typing import Dict, List, Tuple

from misc   import load_json, save_json



class PlaylistSongs:
    file: str

    # <Message ID>: <Song ID>
    byMsgID: Dict[str, str]

    # <Channel ID>:
    #   <Song ID>: [
    #       [<Message ID>],
    #       <Website Type>,
    #       <PlaylistItem ID>
    #   ]
    bySongID: Dict[
        str, Dict[
            str, Tuple[
                List[str],
                str,
                str
            ]
        ]
    ]


    def __init__(self, filepath: str) -> None:
        self.file = filepath

        self.load()



    def load(self):
        self.bySongID = load_json(self.file)

        self.byMsgID = {}

        for _, songID, entryData in self.fetchSongs():
            for msgID in entryData[0]:
                self.byMsgID[msgID] = songID


    def save(self):
        save_json(self.file, self.bySongID)
    


    def fetchSongs(self):
        for channelID, songs in self.bySongID.items():
            for songID, entryData in songs.items():
                yield channelID, songID, entryData