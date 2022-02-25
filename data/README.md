# Introduction
This file serves to explain and document the purposes of the following json files as well as their structures.

# Types

\<Message ID> : ID of the discord message

\<Server ID> : ID of the discord guild/server

\<Song ID> : ID of the song, be it on spotify, youtube or a different site

\<Website Type>: The website the song is on. Stored as one of the WebsiteType values (ex: "youtube")

\<PlaylistItem ID>: Unique ID of the playlist item

# File Explanations

## shared_songs_by_msgID

Stores all the song ids, where the key is the message id. Is useful since we can quickly look up whether a message contains a valid song.

```
{
    <Message ID> : <Song ID>
}
```

## shared_songs_by_songID

Stores all the messages that have shared a song. Is useful because it keeps track of all the messages that have shared a specific song.

```
{
    <Server ID> : {
        <Song ID> : [<Message ID>]
    }
}
```

## playlist_items_by_songID

Stores all the songs that have been added to a playlist. This is needed to remove an item from a playlist once a message has been deleted, since the only way to do this on youtube is by specifying the video's unique `PlaylistItem` id. The reason this is not combined with `shared_songs_by_msgID` is because the structure is different. Some entries in `shared_songs_by_msgID` might not actually be intended to be in a playlist.

```
{
    <Song ID> : [<Website Type>, <PlaylistItem ID>]
}
```