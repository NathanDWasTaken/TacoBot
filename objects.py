from enum import Enum


class MessageType(Enum):
	"""
	The different types of messages there are
	"""
	# A message with an invalid file
	InvalidFile = -2

	# A message with an invalid url
	InvalidUrl  = -1

	# Any Message is accepted
	Any         = 0

	# A message that is none of the above
	Normal      = 1

	# A message that contains any url
	Url         = 2

	# A message that contains a file
	File        = 3


class WebsiteType(Enum):
	"""
	Enum for all currently supported websites
	"""
	YouTube = "youtube"
	Spotify = "spotify"
	Other   = None


class ReactionType(Enum):
	"""
	Enum for all emojis the bot could reply with
	"""
	NO      = -1
	MAYBE   = 0
	YES     = 1
	FIRE    = 2


class MyEmoji:
	def __init__(self, id, name, animated=False) -> None:
		self.id 		= id
		self.name		= name
		self.animated	= animated

		self.full_id	= self.get_full_id()


	def get_full_id(self, id:int=None, name:str=None, animated:bool=None):
		if id is None:
			id = self.id

		if name is None:
			name = self.name

		if animated is None:
			animated = self.animated

		return f"{'a' if animated else ''}:{name}:{id}"



website_domains = {
    "youtu.be"          : WebsiteType.YouTube,
    "youtube.com"       : WebsiteType.YouTube,

    "open.spotify.com"  : WebsiteType.Spotify,
    "spotify.com"       : WebsiteType.Spotify,
}


emoji_ids_per_server = {
	# REAL
	924350783892389939 : {
		ReactionType.FIRE    : MyEmoji(name="fire_asf", id=967765641656410132, animated=True),
		ReactionType.YES     : MyEmoji(name="peepoYES", id=967771488939827240),
		ReactionType.MAYBE   : MyEmoji(name="peepoMAYBE", id=967771488625229854),
		ReactionType.NO      : MyEmoji(name="peepoNO", id=967771488709136454)
	},


	# TEST
	927704499194310717 : {
		ReactionType.FIRE    : MyEmoji(name="fire_asf", id=967777799718977647, animated=True),
		ReactionType.YES     : MyEmoji(name="peepoYES", id=967777790843830292),
		ReactionType.MAYBE   : MyEmoji(name="peepoMAYBE", id=967777790688645170),
		ReactionType.NO      : MyEmoji(name="peepoNO", id=967777790705430538)
	}
}