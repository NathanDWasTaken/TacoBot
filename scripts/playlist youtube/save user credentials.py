# https://stackoverflow.com/questions/21228815/adding-youtube-video-to-playlist-using-python
# (https://stackoverflow.com/questions/22174090/uploading-video-to-youtube-and-adding-it-to-playlist-using-youtube-data-api-v3-i)

import os, pickle


from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Cloud Console at
# https://cloud.google.com/console.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets

CLIENT_SECRETS_FILENAME = "client_secrets.json"

FOLDER                  = os.path.split(__file__)[0]
CLIENT_SECRETS_FILE     = os.path.join(FOLDER, CLIENT_SECRETS_FILENAME)

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

%s

with information from the Cloud Console
https://cloud.google.com/console

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                            CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.upload"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"



credentials_file = "yt channel credentials"


def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=YOUTUBE_SCOPES
    )

    flow.run_local_server()
    credentials = flow.credentials

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)




def add_video_to_playlist(youtube, videoID, playlistID):
    add_video_request=youtube.playlistItems().insert(
    part="snippet",
    body={
        'snippet': {
            'playlistId': playlistID, 
            'resourceId': {
                    'kind': 'youtube#video',
                'videoId': videoID
            }
        #'position': 0
        }
}
    ).execute()

if __name__ == '__main__':
    # youtube = get_authenticated_service()

    # with open(credentials_file, "wb") as file:
    #     pickle.dump(youtube, file)

    with open(credentials_file, "rb") as file:
        youtube = pickle.load(file)

    add_video_to_playlist(youtube, "r-SurvChGFk", "PLBGQSubgZKsZAV3mT6RELLGRmd2L_RP-F")