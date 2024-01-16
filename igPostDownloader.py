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

from googleapiclient.errors import HttpError


from ytDownloader import getFirstEmptyRow

import time
import random

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
    postCaption = ""

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
            str(self.postAccountTags) + "," +
            self.postCaption
        )
        return string
    
    def asList(self):
        return (
            [
            str(self.postShortCode),
            str(self.postDate),
            str(self.postAccount),
            str(self.postType),
            str(self.videoViewCount),
            str(self.postLikes),
            str(self.postComments),
            str(self.postIsSponsored),
            str(self.postSponsors),
            str(self.postHashtags),
            str(self.postAccountTags),
            str(self.postCaption)
            ]
        )

    
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


def setlastIgPostUpdate(listIndex, sheetObject):
    # Set the time that the video record was updated
    cellToUpdate = "Riders!E" + str(listIndex) # lastIgPostUpdate should be in column E of Riders sheet
    body = {
        'values' : [
            [str(date.today())]
        ]
    }
    try:
        response = sheetObject.spreadsheets().values().update(
            spreadsheetId = masterSheetId, 
            range = cellToUpdate, 
            body = body,
            valueInputOption = 'USER_ENTERED').execute()
    except HttpError as e:
        print(e)

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


def updateIgPostRecordsSheet(firstEmptyRow, sheetObject, newIgRecord):
    currentRow = firstEmptyRow
    riderSheetPos = 2 # Riders sheet is sorted prior to updateVideoRecordsSheet() being called. Pos = 2 to start on second row, since first row contains headers

    # newVideoRecords[0] is a YtVideoRecord
    currentRider = newIgRecord.postAccount
    
        
    # # Only increment the ridersheetPost if the rider changes
    # if record.rider != currentRider:
    #     riderSheetPos += 1
    #     currentRider = record.rider
    rowToUpdate = "igPostDb!A" + str(currentRow)
    data = newIgRecord.asList()
    body = {
        'values' : [
            data
        ]
    }
    try:
        response = sheetObject.spreadsheets().values().update(
            spreadsheetId = masterSheetId, 
            range = rowToUpdate, 
            body = body,
            valueInputOption = 'USER_ENTERED').execute()
    except HttpError as e:
        print(e)

    # #update Riders Sheet lastVideoRecordUpdate column (should be column C)
    # setlastVideoRecordUpdate(riderSheetPos,sheetObject)
    # currentRow += 1
    #currentRider = newVideoRecords[currentRow].rider
    
    time.sleep(1.5)

def populateIgPostRecordList(ridersToRecord, sheetObject):
    recordList = []
    ridersheetRow = 2
    dateAfter = datetime.today() - timedelta(days=(1*365)) # Search for videos in last year
    igLoader = loadIgSession()

    # loop through all riders #######
    for rider in ridersToRecord:
        igProfile = instaloader.Profile.from_username(igLoader.context, rider[0])
        print("Retrieving posts for " + rider[0])
        riderPostCount = 0

        # loop through posts for rider #########
        for post in igProfile.get_posts():
            #post.date is datetime
            # if ((post.date < dateAfter) and riderPostCount > 10):
            startDate = datetime(year = 2023, month = 1, day = 1)
            endDate = datetime(year = 2023, month = 12, day = 31)
            if(((post.date > endDate))): # and riderPostCount > 10):
                print("skipped " + str(post.date))
                continue
            if(post.date < startDate):
                break
            record = igPostRecord()
            record.postAccount = rider[0]
            record.postShortCode = post.shortcode
            record.postDate = post.date
            record.postType = post.typename
            if (post.typename == "GraphVideo"):
                record.videoViewCount = post.video_view_count
            record.postLikes = post.likes
            record.postComments = post.comments
            # record.postIsSponsored = post.sponsor_users
            record.postHashtags = str(post.caption_hashtags)
            record.postAccountTags = str(post.tagged_users)
            record.postCaption = post.caption
            # recordList.append
# //////// Instead of appending I am going to try post directly to sheet
            # This is due to the liability of keeping the data in memory when the program is susceptible to crashing because of ig limits
            
            firstEmptyRow = getFirstEmptyRow(sheetObject, "igPostDb")
            updateIgPostRecordsSheet(firstEmptyRow, sheetObject, record)
            print("post added to sheet from " + str(post.date))
            riderPostCount += 1
        
        setlastIgPostUpdate(ridersheetRow,sheetObject)
        ridersheetRow += 1
        print("sleeping from 2-4 minutes")
        time.sleep(random.uniform(120,240))
            # print(post.shortcode)
        

            
    return 0


def main():
    # Create connection to Sheets API
    googleSheet = googleSheetsHelper.getGoogleSheet(sheetsApi, sheetsApiVersion, [], keyFileLocation)

    # Get a list of accounts to get posts for, first sorting by last updated igFollowers
    googleSheetsHelper.sortRiderSheetByLastIgPostUpdate(googleSheet)
    # igAccountsToTrack = googleSheetsHelper.getIgAccountNamesFromNamedSheet(googleSheet,46, "FoxTeam")
    numAccounts = 50
    igAccountsToTrack = googleSheetsHelper.getIgAccountNamesFromNamedSheet(googleSheet,numAccounts, "Riders")


    # Retrieve the posts for each rider
    populateIgPostRecordList(igAccountsToTrack, googleSheet)

main()