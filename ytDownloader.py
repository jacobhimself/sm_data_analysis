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

# import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
# import googleapiclient.errors

import os.path
import csv
from datetime import date, timedelta, timezone
import instaloader
import time
import random
from datetime import datetime
import ytApiKey

import sys

import requests

import isodate

import json


sharedFolderId = "1LrkxznfjcjB2Gmg180FdPF0U3JHyBV-Z"
scope = 'https://www.googleapis.com/auth/drive'
scopeYt = ["https://www.googleapis.com/auth/youtube.force-ssl"]
# scopeSheets = []
youtubeApiKey = ytApiKey.apiKey
youtubeApi = "youtube"
youtubeApiVersion = "v3"

sheetsApi = "sheets"
sheetsApiVersion = "v4"
masterSheetId = "1zyWCq_QgFe8xkCwxULzovpS4LSmIGczoEBZXVCyCKlM"

clientSecret = "client_secret.json"

keyFileLocation = os.path.dirname(os.path.realpath(__file__)) + '/cloud_service_account_key.json'
dateAsString = str(date.today())
handleFileName = "Handles: " + dateAsString + ".csv"
handleFileNamePath =  os.path.dirname(os.path.realpath(__file__)) +  "/handle_files/" + handleFileName 
outputCsvFileName = dateAsString + ".csv"
outputCsvFileNamePath = os.path.dirname(os.path.realpath(__file__))+ "/follower_files/" + outputCsvFileName
startFromBeginning = True


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

        

    def toString(self):
        return (
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
    
    def asList(self):
        return (
            [self.videoId,
            str(self.videoTitle),
            self.rider,
            str(self.publishDate),
            str(self.captureDate),
            self.channelId,
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
    dateAfter = date.today() - timedelta(days=(5 * 365))
    request = ytConnection.search().list(
        part = "snippet",
        order = "relevance",
        q = searchParam,
        publishedAfter = dateAfter
    )
    response = request.execute()
    return response


# Return a service that communicates to Google Drive API
def getMyDrive(api_name, api_version, scopes, key_file_location):
    # Can be adjusted to access other APIs by adjusting the api_name variable

    # Args:
    #     api_name: The name of the api to connect to.
    #     api_version: The api version to connect to.
    #     scopes: A list auth scopes to authorize for the application.
    #     key_file_location: The path to a valid service account JSON key file.

    # Get service account credentials to automate Oauth procedure
    credentials = service_account.Credentials.from_service_account_file(key_file_location)
    scoped_credentials = credentials.with_scopes(scopes)

    # Build the service object.
    service = build(api_name, api_version, credentials=scoped_credentials)

    return service

def getGoogleSheet(api_name, api_version, scopes, key_file_location):
    creds = service_account.Credentials.from_service_account_file(key_file_location)
    service = build(api_name, api_version, credentials=creds)
    return service




# Upload the completed handle,follower csv file to Google Drive
def uploadCsvFile(serviceObject):

    file_metadata = {"name": outputCsvFileName, "parents":[sharedFolderId]}
    media = MediaFileUpload(outputCsvFileNamePath, mimetype="text/csv", resumable=True)
    file = (
        serviceObject.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

def writeToLogFile(message):
    currentDateTime = datetime.now()
    # formattedDateTime = currentDateTime.strftime('%Y-%m-%d %H:%M:%S')
    print(str(datetime.now()) + "    " + message)
    # print(formattedDateTime + "    " + message)

    log_file_path = "Log_" + dateAsString + ".txt"
    with open(log_file_path, 'a') as log_file:
        log_file.write(str(datetime.now()) + message + "\n")




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




def main():
    

    
    # URL = "https://www.googleapis.com/youtube/v3/search"
    # PARAMS = {
    #     "key": 'AIzaSyCGYfwTj1FXK-7Gyoo5-hlxogkIAVUOGGk',
    #     "q": 'bmx',
    #     "type":"video",
    #     "part":"snippet",
    #     "maxResults":50,
    #     "order":"relevance"
    # }

    # r = requests.get(url = URL, params = PARAMS)

    # data = r.json()

    # with open("ytApiSearchResponse.json", "w") as outfile:
    #     json.dump(data, outfile)


    googleSheetObject = getGoogleSheet(sheetsApi, sheetsApiVersion, [], keyFileLocation)
    sortRiderSheetByLastUpdated(googleSheetObject)
    searchTerms = getFirst50SearchTerms(googleSheetObject)["values"] #searchTerms is a list

    # Create Video Record list
    videoRecordList = []

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

    count = 0
    for rider in searchTerms:
        if count < 40:
            print(count)
            # SEARCH RIDER REQUEST
            URL = "https://www.googleapis.com/youtube/v3/search"
            PARAMS = {
                "key": 'AIzaSyCGYfwTj1FXK-7Gyoo5-hlxogkIAVUOGGk',
                "q": rider,
                "type":"video",
                "part":"snippet",
                "maxResults":50,
                # "order":"relevance"
                "order":"viewCount"
            }

            r = requests.get(url = URL, params = PARAMS)
            print(r)
            """
            JSON received from get request looks like:
            {
                
                "kind": "youtube#searchListResponse",
                "etag": "ud_xOlrS2bpdJnkjXUnYCn50f8g",
                "nextPageToken": "CDIQAA",
                "regionCode": "AU",
                "pageInfo": {
                    "totalResults": 1000000,
                    "resultsPerPage": 50
                },
                "items": [
                    {
                        "kind": "youtube#searchResult",
                        "etag": "9lI-3zHaTFYMyvuVH-w_WvtnnLU",
                        "id": {
                            "kind": "youtube#video",
                            "videoId": "bjO1S9eHgEI"
                        },
                        "snippet": {
                            "publishedAt": "2023-11-23T16:00:07Z",
                            "channelId": "UCJHbVOD6qHuwkTth4Nn38PQ",
                            "title": "FEAST | Odyssey BMX",
                            "description": "It's time to FEAST! Enjoy over 15-minutes of the Odyssey crew with dedicated parts from Boyd Hilder, Santi Laverde and Mikey ...",
                            "thumbnails": {
                                "default": {
                                    "url": "https://i.ytimg.com/vi/bjO1S9eHgEI/default.jpg",
                                    "width": 120,
                                    "height": 90
                                },
                                "medium": {
                                    "url": "https://i.ytimg.com/vi/bjO1S9eHgEI/mqdefault.jpg",
                                    "width": 320,
                                    "height": 180
                                },
                                "high": {
                                    "url": "https://i.ytimg.com/vi/bjO1S9eHgEI/hqdefault.jpg",
                                    "width": 480,
                                    "height": 360
                                }
                            },
                            "channelTitle": "Odyssey BMX",
                            "liveBroadcastContent": "none",
                            "publishTime": "2023-11-23T16:00:07Z"
                        }
                    },
                    {record2},
                    {record3}.
                ]
            }
            
            """

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
                    "key": 'AIzaSyCGYfwTj1FXK-7Gyoo5-hlxogkIAVUOGGk',
                    "part": "snippet, statistics, contentDetails",
                    "id": record.videoId,
                }

                r = requests.get(url = URL, params = PARAMS)
                print("retrieving video record for " + str(record.videoTitle))
                # print("videoId = " + videoId)
                # print(type(videoId))
                # print(r)
                # result = r.json()
                # # print(result)
                # # print(type(result))
                result = r.json()["items"]
                videoData = result[0]
                print("retrieved: ")
                print(videoData["snippet"]["title"])


                try:
                    #set video length property, extracting length from the "PT3M49S" ISO8601 format and setting it in seconds
                    # isovideoDuration = isodate.parse_duration(videoData["contentDetails"]["duration"]).total_seconds()
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
                videoRecordList.append(record)
                print(record)



                print("Appended " + record.rider + " - " + record.videoTitle)
                print("Length of videoRecord List is: " + str(len(videoRecordList)))
        count += 1
    
    # SAVE THE RECORD AS A CSV SO I DON'T HAVE TO KEEP MAKING CALLS TO THE API. ONCE THIS IS DONE, FIGURE OUT HOW TO SEND THE VIDEO RECORDS DIRECTLY TO GOOGLE SHEET
    file_name = "videoRecordList_02.csv"

    with open(file_name, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "videoId",
            "videoTitle",
            "rider",
            "publishDate",
            "captureDate",
            "channelId",
            "channelTitle",
            "videoDuration (seconds)",
            "videoDefinition",
            "videoViewCount",
            "videoLikeCount",
            "videoFavoriteCount",
            "videoCommentCount"
            ])
        for record in videoRecordList:
            writer.writerow(record.asList())



# def asList(self):
#         return (
#             [self.videoId,
#             str(self.videoTitle),
#             self.rider,
#             str(self.publishDate),
#             str(self.captureDate),
#             self.channelId,
#             str(self.channelTitle),
#             str(self.videoDuration),
#             str(self.videoDefinition),
#             str(self.videoViewCount),
#             str(self.videoLikeCount),
#             str(self.videoFavoriteCount),
#             str(self.videoCommentCount)
#             ]
#         )
    # for record in videoRecordList:
    #     print("Rider: " + record.rider + ", Video: " + record.videoTitle)

        # get search results

        #       iterate through search results
        #           create YtVideoRecord() with properties available from search
        #           make a request to get video stats based on videoID
        #           finish remaining properties with result




















    # # for i in searchTerms:
    # #     print(i[0]) #Search Term
    # #     record = YtVideoRecord()
    # #     record.rider = i[0]
    # aaronRoss = (searchTerms[0])
    
    # # SEARCH RIDER REQUEST
    # URL = "https://www.googleapis.com/youtube/v3/search"
    # PARAMS = {
    #     "key": 'AIzaSyCGYfwTj1FXK-7Gyoo5-hlxogkIAVUOGGk',
    #     "q": aaronRoss,
    #     "type":"video",
    #     "part":"snippet",
    #     "maxResults":50,
    #     "order":"relevance"
    # }

    # r = requests.get(url = URL, params = PARAMS)

    # """
    # JSON received from get request looks like:
    # {
        
    #     "kind": "youtube#searchListResponse",
    #     "etag": "ud_xOlrS2bpdJnkjXUnYCn50f8g",
    #     "nextPageToken": "CDIQAA",
    #     "regionCode": "AU",
    #     "pageInfo": {
    #         "totalResults": 1000000,
    #         "resultsPerPage": 50
    #     },
    #     "items": [
    #         {
    #             "kind": "youtube#searchResult",
    #             "etag": "9lI-3zHaTFYMyvuVH-w_WvtnnLU",
    #             "id": {
    #                 "kind": "youtube#video",
    #                 "videoId": "bjO1S9eHgEI"
    #             },
    #             "snippet": {
    #                 "publishedAt": "2023-11-23T16:00:07Z",
    #                 "channelId": "UCJHbVOD6qHuwkTth4Nn38PQ",
    #                 "title": "FEAST | Odyssey BMX",
    #                 "description": "It's time to FEAST! Enjoy over 15-minutes of the Odyssey crew with dedicated parts from Boyd Hilder, Santi Laverde and Mikey ...",
    #                 "thumbnails": {
    #                     "default": {
    #                         "url": "https://i.ytimg.com/vi/bjO1S9eHgEI/default.jpg",
    #                         "width": 120,
    #                         "height": 90
    #                     },
    #                     "medium": {
    #                         "url": "https://i.ytimg.com/vi/bjO1S9eHgEI/mqdefault.jpg",
    #                         "width": 320,
    #                         "height": 180
    #                     },
    #                     "high": {
    #                         "url": "https://i.ytimg.com/vi/bjO1S9eHgEI/hqdefault.jpg",
    #                         "width": 480,
    #                         "height": 360
    #                     }
    #                 },
    #                 "channelTitle": "Odyssey BMX",
    #                 "liveBroadcastContent": "none",
    #                 "publishTime": "2023-11-23T16:00:07Z"
    #             }
    #         },
    #         {record2},
    #         {record3}.
    #     ]
    # }
    
    # """

    # searchResults = r.json()["items"]
    # # print(type(searchResults[0]))
    # videoId = searchResults[0]["id"]["videoId"]
    # # for result in searchResults:
    # #     print(result["id"]["videoId"])
    # #     print(result["snippet"]["title"])

    # # GET VIDEO DETAILS REQUEST
    # URL = "https://www.googleapis.com/youtube/v3/videos"
    # PARAMS = {
    #     "key": 'AIzaSyCGYfwTj1FXK-7Gyoo5-hlxogkIAVUOGGk',
    #     "part": "snippet, statistics, contentDetails",
    #     "id": videoId,
    # }

    # r = requests.get(url=URL, params=PARAMS)
    # print("videoId = " + videoId)
    # print(type(videoId))
    # print(r)
    # # result = r.json()
    # # print(result)
    # # print(type(result))
    # result = r.json()["items"]
    # videoData = result[0]
    # print(videoData["snippet"]["title"])


















    # record = searchResults[0] # currently a dict
    # print(record["id"])
    # print(type(record["id"]))
    # print(record["id"]["videoId"])


    # testRecord = YtVideoRecord()
    # testRecord.videoId = data["id"]["videoId"]
    # testRecord.videoId = (data[2])[1] # [2] is "id", [1] is "videoId"
    # # For following fields [3] is "snippet"
    # testRecord.videoTitle = [3][2] # [2] is "title"
    # testRecord.rider = aaronRoss
    # testRecord.publishDate = [3][0] # [0] is "publishedAt"
    # testRecord.channelId = [3][1] # [1] is "channelId"
    # testRecord.channelTitle = [3][5] # [5] is "channelTitle"

    # print(vars(testRecord))


    # class YtVideoRecord:
    # videoId = ""
    # videoTitle = ""
    # rider = ""
    # publishDate = datetime.utcfromtimestamp(0)
    # captureDate = datetime.now()
    # channelId = ""
    # channelTitle = ""
    # videoDuration = -1
    # videoDefinition = ""
    # videoViewCount = -1
    # videoLikeCount = -1
    # videoFavoriteCount = -1
    # videoCommentCount = -1

    


    





    # ############################################


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
    
    
    


main()
