"""
Author: Jacob France
Date: 20/12/2023
File Description:
Instagram follower counts alone do not tell a complete picture of online performance and marketability. Youtube videos are a common form of promotion in the action sports industry
and I have decided to use video performance to supplement the data obtained from instagram
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload


import os.path
import csv
from datetime import date, timedelta
from datetime import datetime
import ytApiKey


import requests

import isodate


sharedFolderId = "1LrkxznfjcjB2Gmg180FdPF0U3JHyBV-Z"
scope = 'https://www.googleapis.com/auth/drive'
scopeYt = ["https://www.googleapis.com/auth/youtube.force-ssl"]
youtubeApiKey = ytApiKey.apiKey
youtubeApi = "youtube"
youtubeApiVersion = "v3"

sheetsApi = "sheets"
sheetsApiVersion = "v4"
masterSheetId = "1zyWCq_QgFe8xkCwxULzovpS4LSmIGczoEBZXVCyCKlM"

clientSecret = "client_secret.json"

keyFileLocation = os.path.dirname(os.path.realpath(__file__)) + '/cloud_service_account_key.json'
dateAsString = str(date.today())


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

        

    # def toString(self):
    #     return (
    #         self.videoId + "," +
    #         self.videoTitle + "," +
    #         self.rider + "," +
    #         str(self.publishDate) + "," +
    #         str(self.captureDate) + "," +
    #         self.channelId + "," +
    #         self.channelTitle + "," +
    #         str(self.videoDuration) + "," +
    #         self.videoDefinition + "," +
    #         str(self.videoViewCount) + "," +
    #         str(self.videoLikeCount) + "," +
    #         str(self.videoFavoriteCount) + "," +
    #         str(self.videoCommentCount)
    #     )
    
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


def youtubeSearch(ytConnection, searchParam):
    dateAfter = date.today() - timedelta(days=(10* 365)) # Search for videos in last ten years
    request = ytConnection.search().list(
        part = "snippet",
        order = "relevance",
        q = searchParam,
        publishedAfter = dateAfter
    )
    response = request.execute()
    return response


# # Return a service that communicates to Google Drive API
# def getMyDrive(api_name, api_version, scopes, key_file_location):
#     # Can be adjusted to access other APIs by adjusting the api_name variable

#     # Args:
#     #     api_name: The name of the api to connect to.
#     #     api_version: The api version to connect to.
#     #     scopes: A list auth scopes to authorize for the application.
#     #     key_file_location: The path to a valid service account JSON key file.

#     # Get service account credentials to automate Oauth procedure
#     credentials = service_account.Credentials.from_service_account_file(key_file_location)
#     scoped_credentials = credentials.with_scopes(scopes)

#     # Build the service object.
#     service = build(api_name, api_version, credentials=scoped_credentials)

#     return service

def getGoogleSheet(api_name, api_version, scopes, key_file_location):
    creds = service_account.Credentials.from_service_account_file(key_file_location)
    service = build(api_name, api_version, credentials=creds)
    return service




# # Upload the completed handle,follower csv file to Google Drive
# def uploadCsvFile(serviceObject):

#     file_metadata = {"name": outputCsvFileName, "parents":[sharedFolderId]}
#     media = MediaFileUpload(outputCsvFileNamePath, mimetype="text/csv", resumable=True)
#     file = (
#         serviceObject.files()
#         .create(body=file_metadata, media_body=media, fields="id")
#         .execute()
#     )

# def writeToLogFile(message):
#     currentDateTime = datetime.now()
#     # formattedDateTime = currentDateTime.strftime('%Y-%m-%d %H:%M:%S')
#     print(str(datetime.now()) + "    " + message)
#     # print(formattedDateTime + "    " + message)

#     log_file_path = "Log_" + dateAsString + ".txt"
#     with open(log_file_path, 'a') as log_file:
#         log_file.write(str(datetime.now()) + message + "\n")




def getFirst50SearchTerms(serviceObject):
    try:

        result = (
            serviceObject.spreadsheets()
            .values()
            .get(spreadsheetId=masterSheetId, range="Riders!B2:B51")
            .execute()
        )
        rows = result.get("values", [])
        print(f"{len(rows)} rows retrieved")
        for row in rows:
            print(row)
        return result
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

    # iterate through  list of search terms. Based on usage in main() this should be 50 terms
    # For each search term, there will be 50 results from the youtube search.
    # For 50 search terms, this should use 7500 out of 10,000 available API credits
    # Searches are worth 100 credits, individual video data is worth 1 credit
    for rider in searchTermList:
        if count < 50:
            print(count)
            # SEARCH RIDER REQUEST
            URL = "https://www.googleapis.com/youtube/v3/search"
            PARAMS = {
                "key": youtubeApiKey,
                "q": str(rider) + "bmx",
                "type":"video",
                "part":"snippet",
                "maxResults":50,
                # "order":"relevance"
                "order":"viewCount"
            }

            r = requests.get(url = URL, params = PARAMS)
            print(r)
            searchResults = r.json()["items"]

            for result in searchResults:
                # START BY GETTING THE INFORMATION AVAILABLE FROM THE INITIAL SEARCH
                record = YtVideoRecord()
                record.rider = str(rider)
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

def updateVideoRecordsSheet(firstEmptyRow, sheetObject, newVideoRecords):
    currentRow = firstEmptyRow
    for record in newVideoRecords:
        rowToUpdate = "VideoRecords!A" + str(currentRow) 
        body = {
            'values' : [
                record.asList()
            ]
        }
        try:
            response = sheetObject.spreadsheets().values().update(
                spreadsheetId = masterSheetId, 
                range = rowToUpdate, 
                body = body,
                valueInputOption = 'RAW').execute()
        except HttpError as e:
            print(e)
        currentRow += 1

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
    # sortRiderSheetByLastUpdated(googleSheetObject)
    searchTerms = getFirst50SearchTerms(googleSheetObject)["values"] #searchTerms is a list

    # Populate Video Record list via Youtube API
    # videoRecordList = populateVideoRecordList(searchTerms)

    firstEmptyRow = getFirstEmptyRow(googleSheetObject, "VideoRecords")
    # Push video record list to Google Sheet
    newRecord = YtVideoRecord()
    updateVideoRecordsSheet(firstEmptyRow, googleSheetObject, [newRecord])


    # 2. Add search term to dict as key, with another empty dict as value
    # riderVideoDict = {}

    # for rider in searchTerms:
    #     riderVideoDict[str(rider)] = {}

    #3. For each rider, get a search result with 50 results
    #       for each result, create a ytVideoRecord and set the properties for:
    #           videoId
    #           videoTitle
    #           Rider (search term)
    #           publishDate (date video was published)
    #           captureDate (defaults to today)
    #           channelID
    #           channelTitle
    # recordList = []
    # count = 0
    # for rider in searchTerms:
    #     if count < 40:
    #         print(count)
    #         # SEARCH RIDER REQUEST
    #         URL = "https://www.googleapis.com/youtube/v3/search"
    #         PARAMS = {
    #             "key": youtubeApiKey,
    #             "q": rider,
    #             "type":"video",
    #             "part":"snippet",
    #             "maxResults":50,
    #             # "order":"relevance"
    #             "order":"viewCount"
    #         }

    #         r = requests.get(url = URL, params = PARAMS)
    #         print(r)
    #         searchResults = r.json()["items"]

    #         for result in searchResults:
    #             # START BY GETTING THE INFORMATION AVAILABLE FROM THE INITIAL SEARCH
    #             record = YtVideoRecord()
    #             record.rider = str(rider)
    #             record.videoId = result["id"]["videoId"]
    #             record.videoTitle = result["snippet"]["title"]
    #             record.publishDate = result["snippet"]["publishedAt"]
    #             record.channelId = result["snippet"]["channelId"]
    #             record.channelTitle = result["snippet"]["channelTitle"]

    #             # THEN MAKE A REQUEST FOR THE VIDEO BASED ON THE VIDEO ID AND COMPLETE THE RECORD

    #             # GET VIDEO DETAILS REQUEST
    #             URL = "https://www.googleapis.com/youtube/v3/videos"
    #             PARAMS = {
    #                 "key": youtubeApiKey,
    #                 "part": "snippet, statistics, contentDetails",
    #                 "id": record.videoId,
    #             }

    #             r = requests.get(url = URL, params = PARAMS)
    #             print("retrieving video record for " + str(record.videoTitle))
    #             result = r.json()["items"]
    #             videoData = result[0]
    #             print("retrieved: ")
    #             print(videoData["snippet"]["title"])


    #             try:
    #                 #set video length property, extracting length from the "PT3M49S" ISO8601 format and setting it in seconds
    #                 # isovideoDuration = isodate.parse_duration(videoData["contentDetails"]["duration"]).total_seconds()
    #                 videoLength = isodate.parse_duration(videoData["contentDetails"]["duration"]).total_seconds()
    #                 record.videoDuration = videoLength
    #                 record.videoDefinition = videoData["contentDetails"]["definition"]
    #                 record.videoViewCount = videoData["statistics"]["viewCount"]
    #                 record.videoLikeCount = videoData["statistics"]["likeCount"]
    #                 record.videoFavoriteCount = videoData["statistics"]["favoriteCount"]
    #                 record.videoCommentCount = videoData["statistics"]["commentCount"]

    #             except KeyError as e:
    #                 print("Key Error. Not all fields retrieved. Check data for default values")
    #                 print(e)


    #             # APPEND THE VIDEO RECORD TO THE VIDEO RECORD LIST ONCE ALL FIELDS HAVE BEEN COMPLETED
    #             videoRecordList.append(record)
    #             print(record)
    #             print("Appended " + record.rider + " - " + record.videoTitle)
    #             print("Length of videoRecord List is: " + str(len(videoRecordList)))
    #     count += 1
    
    # SAVE THE RECORD AS A CSV SO I DON'T HAVE TO KEEP MAKING CALLS TO THE API. ONCE THIS IS DONE, FIGURE OUT HOW TO SEND THE VIDEO RECORDS DIRECTLY TO GOOGLE SHEET
    # file_name = "videoRecordList_02.csv"

    # with open(file_name, "w", newline="") as file:
    #     writer = csv.writer(file)
    #     writer.writerow([
    #         "videoId",
    #         "videoTitle",
    #         "rider",
    #         "publishDate",
    #         "captureDate",
    #         "channelId",
    #         "channelTitle",
    #         "videoDuration (seconds)",
    #         "videoDefinition",
    #         "videoViewCount",
    #         "videoLikeCount",
    #         "videoFavoriteCount",
    #         "videoCommentCount"
    #         ])
    #     for record in videoRecordList:
    #         writer.writerow(record.asList())























    
    
    


main()
