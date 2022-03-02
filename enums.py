from enum import Enum


class MessageType(Enum):
    """
    The different types of messages there are
    """
    # A message with an invalid file
    InvalidFile = -2

    # A message with an invalid url
    InvalidUrl  = -1

    # A message that is none of the above
    Normal      = 0

    # A message that contains any url
    Url         = 1

    # A message that contains a file
    File        = 2


class WebsiteType(Enum):
    """
    Enum for all currently supported websites
    """
    YouTube = "youtube"
    Spotify = "spotify"
    Other   = None