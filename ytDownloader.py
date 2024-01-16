"""
Author: Jacob France
Date: 20/12/2023
File Description:
Instagram follower counts alone do not tell a complete picture of online performance and marketability. Youtube videos are a common form of promotion in the action sports industry
and I have decided to use video performance to supplement the data obtained from instagram

A brief summary:
1 - A list of bmx rider names is pulled from a Google Sheet via the Sheets api
2 - The list is looped through, with " bmx" being appended to each riders name before using the Youtube api search.list() endpoint to get the 50 most viewed videos for that rider's name
3 - For each search term, all 50 videos are looped through, with stats for each video, such as view count, like count, comment count, etc being obtained with a call to the videos (not video - singular) endpoint.
4 - A list of the YtVideoRecord class is used to hold all records and fields being captured in steps 2 and 3. Once the loops have completed, each item of the list is pushed to a Google sheet via
    the Sheets api. (Please note: a timer is used to slow down the process of pushing the records as there is an api limit of 60 requests per minute)
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account


import os.path
from datetime import date, timedelta
from datetime import datetime, timezone
import ytApiKey


import requests

import isodate
import time



youtubeApiKey = ytApiKey.apiKey
youtubeApi = "youtube"
youtubeApiVersion = "v3"

sheetsApi = "sheets"
sheetsApiVersion = "v4"
masterSheetId = "1zyWCq_QgFe8xkCwxULzovpS4LSmIGczoEBZXVCyCKlM"

keyFileLocation = os.path.dirname(os.path.realpath(__file__)) + '/cloud_service_account_key.json'
dateAsString = str(date.today())

numYoutubeSearches = 1


class YtVideoRecord:
    videoId = ""
    videoTitle = ""
    rider = ""
    publishDate = datetime.utcfromtimestamp(0)
    captureDate = datetime.now()
    channelId = ""
    channelTitle = ""
    videoDuration = -1
    videoDefinition = ""
    videoViewCount = -1
    videoLikeCount = -1
    videoFavoriteCount = -1
    videoCommentCount = -1

    def __str__(self):
        string=(
            self.videoId + "," +
            self.videoTitle + "," +
            self.rider + "," +
            str(self.publishDate) + "," +
            str(self.captureDate) + "," +
            self.channelId + "," +
            self.channelTitle + "," +
            str(self.videoDuration) + "," +
            self.videoDefinition + "," +
            str(self.videoViewCount) + "," +
            str(self.videoLikeCount) + "," +
            str(self.videoFavoriteCount) + "," +
            str(self.videoCommentCount)
        )
        return string
    
    def asList(self):
        return (
            [
            str(self.videoId),
            str(self.videoTitle),
            str(self.rider),
            str(self.publishDate),
            str(self.captureDate),
            str(self.channelId),
            str(self.channelTitle),
            str(self.videoDuration),
            str(self.videoDefinition),
            str(self.videoViewCount),
            str(self.videoLikeCount),
            str(self.videoFavoriteCount),
            str(self.videoCommentCount)
            ]
        )


def getGoogleSheet(api_name, api_version, scopes, key_file_location):
    creds = service_account.Credentials.from_service_account_file(key_file_location)
    service = build(api_name, api_version, credentials=creds)
    return service

def getSearchTerms(serviceObject, numSearches):
    try:
        lastRow = str(1 + numSearches)
        result = (
            serviceObject.spreadsheets()
            .values()
            .get(spreadsheetId=masterSheetId, range="Riders!B2:G" + lastRow) # Column G contains the sport column, this is used to search for name + sport in YouTube search
            .execute()
        )
        rows = result.get("values", [])
        print(f"{len(rows)} rows retrieved")
        for row in rows:
            print(row)
        # return result
        return rows
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

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
                        "dimensionIndex":2,
                        "sortOrder": "ASCENDING"
                    }
                ]
            }
        }
    ]
    }


    res = serviceObject.spreadsheets().batchUpdate(body=requests, spreadsheetId=masterSheetId).execute()

def populateVideoRecordList(searchTermList):
    recordList = []
    count = 0
    # dateAfter = date.today() - timedelta(days=(10* 365)) # Search for videos in last ten years
    dateAfter = (datetime.now(timezone.utc) - timedelta(5*365)).isoformat()

    # iterate through  list of search terms.
    # Each search term will return up to 50 results from the youtube search.
    # 
    # Searches are worth 100 credits, individual video data is worth 1 credit
    # For 50 search terms, this should use 7500 out of 10,000 available API credits
    for rider in searchTermList:
        if count < numYoutubeSearches:
            print(count)
            
            # SEARCH RIDER REQUEST
            URL = "https://www.googleapis.com/youtube/v3/search"
            PARAMS = {
                "key": youtubeApiKey,
                # "q": str(rider[0]),
                "q": str(rider[0]) + " " + str(rider[5]), # rider [5] is adding the "sport" column to the search. For example, "Chase Hawk" + "BMX"
                "type":"video",
                "part":"snippet",
                "maxResults":50,
                # "order":"relevance",
                "order":"viewCount",
                "publishedAfter": str(dateAfter)
            }

            r = requests.get(url = URL, params = PARAMS)
            print(r)
            searchResults = r.json()["items"]

            for result in searchResults:
                # START BY GETTING THE INFORMATION AVAILABLE FROM THE INITIAL SEARCH
                record = YtVideoRecord()
                record.rider = str(rider[0])
                record.videoId = result["id"]["videoId"]
                record.videoTitle = result["snippet"]["title"]
                record.publishDate = result["snippet"]["publishedAt"]
                record.channelId = result["snippet"]["channelId"]
                record.channelTitle = result["snippet"]["channelTitle"]

                # THEN MAKE A REQUEST FOR THE VIDEO BASED ON THE VIDEO ID AND COMPLETE THE RECORD

                # GET VIDEO DETAILS REQUEST
                URL = "https://www.googleapis.com/youtube/v3/videos"
                PARAMS = {
                    "key": youtubeApiKey,
                    "part": "snippet, statistics, contentDetails",
                    "id": record.videoId,
                }

                r = requests.get(url = URL, params = PARAMS)
                print("retrieving video record for " + str(record.videoTitle))
                result = r.json()["items"]
                videoData = result[0]
                print("retrieved: ")
                print(videoData["snippet"]["title"])


                try:
                    #set video length property, extracting length from the "PT3M49S" ISO8601 format and setting it in seconds
                    videoLength = isodate.parse_duration(videoData["contentDetails"]["duration"]).total_seconds()
                    record.videoDuration = videoLength
                    record.videoDefinition = videoData["contentDetails"]["definition"]
                    record.videoViewCount = videoData["statistics"]["viewCount"]
                    record.videoLikeCount = videoData["statistics"]["likeCount"]
                    record.videoFavoriteCount = videoData["statistics"]["favoriteCount"]
                    record.videoCommentCount = videoData["statistics"]["commentCount"]

                except KeyError as e:
                    print("Key Error. Not all fields retrieved. Check data for default values")
                    print(e)


                # APPEND THE VIDEO RECORD TO THE VIDEO RECORD LIST ONCE ALL FIELDS HAVE BEEN COMPLETED
                recordList.append(record)
                print(record)
                print("Appended " + record.rider + " - " + record.videoTitle)
                print("Length of videoRecord List is: " + str(len(recordList)))
        count += 1
    return recordList

def setlastVideoRecordUpdate(listIndex, sheetObject):
    # Set the time that the video record was updated
    cellToUpdate = "Riders!C" + str(listIndex) # lastVideoRecordUpdate should be in column C of Riders sheet
    body = {
        'values' : [
            [dateAsString]
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

def updateVideoRecordsSheet(firstEmptyRow, sheetObject, newVideoRecords):
    currentRow = firstEmptyRow
    riderSheetPos = 2 # Riders sheet is sorted prior to updateVideoRecordsSheet() being called. Pos = 2 to start on second row, since first row contains headers

    # newVideoRecords[0] is a YtVideoRecord
    currentRider = newVideoRecords[0].rider
    # Add each record to the first empty row of the VideoRecords Google Sheet
    for record in newVideoRecords:
        
        # Only increment the ridersheetPost if the rider changes
        if record.rider != currentRider:
            riderSheetPos += 1
            currentRider = record.rider
        rowToUpdate = "VideoRecords!A" + str(currentRow)
        data = record.asList()
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

        #update Riders Sheet lastVideoRecordUpdate column (should be column C)
        setlastVideoRecordUpdate(riderSheetPos,sheetObject)
        currentRow += 1
        #currentRider = newVideoRecords[currentRow].rider
        
        time.sleep(1.5)

def getFirstEmptyRow(sheetObject, sheetName):
    recordRange = sheetName + "!A1:A"
    try:
        result = (
            sheetObject.spreadsheets()
            .values()
            .get(spreadsheetId=masterSheetId, range=recordRange)
            .execute()
        )
        videoIds = result.get("values", [])

        return len(videoIds) + 1

    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

def main():
    
    googleSheetObject = getGoogleSheet(sheetsApi, sheetsApiVersion, [], keyFileLocation)
    sortRiderSheetByLastUpdated(googleSheetObject)
    # searchTerms = getSearchTerms(googleSheetObject)["values"] #searchTerms is a list
    searchTerms = getSearchTerms(googleSheetObject, numYoutubeSearches) #searchTerms is a list


    # Populate Video Record list via Youtube API
    videoRecordList = populateVideoRecordList(searchTerms)

    # Push video record list to Google Sheet
    # lastIgFollowerUpdate column is updated inside updateVideoRecordsSheet() below
    firstEmptyRow = getFirstEmptyRow(googleSheetObject, "VideoRecords")
    updateVideoRecordsSheet(firstEmptyRow, googleSheetObject, videoRecordList)



    
if __name__ == "__main__":
    main()
