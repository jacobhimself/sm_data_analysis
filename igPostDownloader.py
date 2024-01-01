"""
Author: Jacob France
Date: 01/01/2024
File Description:
To help further analyse the social media performance of tracked accounts, a way of tracking post engagement over time needed to be created.
The aim of this script is to store the following fields in a google sheet
- Post shortcode
- Post date
- Post owner
- Post type (pic, vid, sidecar)
- Videoviewcount (for video posts)
- Post Likes
- Post Comments
- Post is sponsored?
- Post sponsors - If sponsored
- Post Hashtags
- Post Account tags
"""


import instaloader

import googleSheetsHelper
import os.path
from datetime import datetime
from datetime import date, timedelta

# from igDownloader import loadIgSession

sheetsApi = "sheets"
sheetsApiVersion = "v4"
masterSheetId = "1zyWCq_QgFe8xkCwxULzovpS4LSmIGczoEBZXVCyCKlM"

# Google Sheet Info
sheetsApi = "sheets"
sheetsApiVersion = "v4"
masterSheetId = "1zyWCq_QgFe8xkCwxULzovpS4LSmIGczoEBZXVCyCKlM"
keyFileLocation = os.path.dirname(os.path.realpath(__file__)) + '/cloud_service_account_key.json'

class igPostRecord:
    postShortCode = ""
    postDate = datetime.utcfromtimestamp(0)
    postAccount = ""
    postType = ""
    videoViewCount = -1
    postLikes = -1
    postComments = -1
    postIsSponsored = False
    postSponsors = []
    postHashtags = []
    postAccountTags = []

    def __str__(self):
        string=(
            self.postShortCode + "," +
            self.postDate + "," +
            self.postAccount + "," +
            self.postType + "," +
            str(self.videoViewCount) + "," +
            str(self.postLikes) + "," +
            str(self.postComments) + "," +
            str(self.postIsSponsored) + "," +
            str(self.postSponsors) + "," +
            str(self.postHashtags) + "," +
            str(self.postAccountTags) + ","
        )
        return string
    
def sortRiderSheetByLastUpdated(serviceObject):

    requests = {
    "requests": [
        {
            "sortRange": {
                "range": {
                    "sheetId": "92107300",
                    "startRowIndex": 1,
                    "startColumnIndex": 0
                },
                "sortSpecs": [
                    {
                        "dimensionIndex":4,
                        "sortOrder": "ASCENDING"
                    }
                ]
            }
        }
    ]
    }


    res = serviceObject.spreadsheets().batchUpdate(body=requests, spreadsheetId=masterSheetId).execute()


# Use instaloader module to retrieve follower data, save the data in follower_files/"todaysFile"
def loadIgSession():
    # Retrieve existing session so that Instagram IP address check is bypassed
    # If Instagram suspects suspicious activity, they will require a manual verification
    # A new session can be created with the instructions in 403_error_login_workaround.py
    USER = "jefethesecond"
    SESSION = "session-jefethesecond"
    try:
        loader = instaloader.Instaloader()
        loader.load_session_from_file(USER,SESSION)
    
    except Exception as e:
        print(f'An error occurred while loading instaloader session: {e}')

    return loader

def populateIgPostRecordList(ridersToRecord=[]):
    recordList = []
    count = 0
    dateAfter = date.today() - timedelta(days=(1*365)) # Search for videos in last year
    igLoader = loadIgSession()

    for rider in ridersToRecord:
        igProfile = instaloader.Profile.from_username(igLoader.context, rider[0])
        print("Retrieving posts for " + rider[0])

        for post in igProfile.get_posts():
            record = igPostRecord()
            record.postAccount = rider
            record.postShortCode = post.shortcode
            print(post.shortcode)
            break
    return 0


def main():
    # Create connection to Sheets API
    googleSheet = googleSheetsHelper.getGoogleSheet(sheetsApi, sheetsApiVersion, [], keyFileLocation)

    # Get a list of accounts to get posts for
    igAccountsToTrack = googleSheetsHelper.getIgAccountNamesFromNamedSheet(googleSheet,46, "FoxTeam")

    # Retrieve the posts for each rider
    populateIgPostRecordList(igAccountsToTrack)

main()