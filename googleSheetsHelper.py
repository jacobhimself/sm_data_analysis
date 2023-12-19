"""
Author: Jacob France
Date: 19/12/2023
File Description:
This file aims to provied functionality to read from and write to a specified Google Sheet directly. Previous versions of this project
relied on a distributed process of using apps script to save a csv file to a google drive, downloading that file and editing it with python
and then uploading to the drive, before apps script picked it up again and added the edited csv to the sheet. While this worked, it spread the 
functionality out too much and had too many steps.
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

import os.path
from datetime import date



sheetsApi = "sheets"
sheetsApiVersion = "v4"
masterSheetId = "1zyWCq_QgFe8xkCwxULzovpS4LSmIGczoEBZXVCyCKlM"


keyFileLocation = os.path.dirname(os.path.realpath(__file__)) + '/cloud_service_account_key.json'
dateAsString = str(date.today())



def getGoogleSheet(api_name, api_version, scopes, key_file_location):
    creds = service_account.Credentials.from_service_account_file(key_file_location)
    service = build(api_name, api_version, credentials=creds)
    return service

def sortRiderSheetByLastIgFollowerUpdate(serviceObject):

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
                        "dimensionIndex":3, # this should be the lastIgFollowerUpdate field
                        "sortOrder": "ASCENDING"
                    }
                ]
            }
        }
    ]
    }


    res = serviceObject.spreadsheets().batchUpdate(body=requests, spreadsheetId=masterSheetId).execute()

def getIgAccountNames(sheetObject, numAccounts = 100):
    # Return a list that contains the number of instragram account handles specified
    accountRange = "Riders!A2:A" + str(numAccounts) #ig handles should be in A column
    try:
        result = (
            sheetObject.spreadsheets()
            .values()
            .get(spreadsheetId=masterSheetId, range=accountRange)
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
    

def getTodaysColumnIndex(sheetObject):
     # Find column number for today's date
    accountRange = "MasterSheet!B1:ZZZ1"
    try:
        result = (
            sheetObject.spreadsheets()
            .values()
            .get(spreadsheetId=masterSheetId, range=accountRange)
            .execute()
        )
        dates = result.get("values", [])
        print(f"{len(dates)} dates retrieved")
        for row in dates:
            print(row)
        print("column index for today is: " + str(len(dates[0])))

        #convert the column index into a string. ie. 49 = "AX"
        result = ""
        index = len(dates[0]) + 2
        while index > 0:
            index -= 1
            result = chr(index % 26 + ord('A')) + result
            index //= 26
        print(result)
        return result

    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

    
def setMasterSheetDateHeader(sheetObject, todaysColumn):

    todaysDateHeaderCell = "MasterSheet!" + todaysColumn + "1"
    body = {
        'values' : [
            [dateAsString]
        ]
    }
    try:
        response = sheetObject.spreadsheets().values().update(
            spreadsheetId = masterSheetId, 
            range = todaysDateHeaderCell, 
            body = body,
            valueInputOption = 'USER_ENTERED').execute()
    except HttpError as e:
        print(e)
        print("Date not set for " + dateAsString)

def setFollowerCountFromListPos(listIndex, colIndex, sheetObject, followerCount):
    rowNum = listIndex + 2
    cellToUpdate = "MasterSheet!" + colIndex + str(rowNum)
    body = {
        'values' : [
            [int(followerCount)]
        ]
    }
    try:
        response = sheetObject.spreadsheets().values().update(
            spreadsheetId = masterSheetId, 
            range = cellToUpdate, 
            body = body,
            valueInputOption = 'RAW').execute()
    except HttpError as e:
        print(e)



def main():
        # Get the Google Sheet Object
        googleSheetObject = getGoogleSheet(sheetsApi, sheetsApiVersion, [], keyFileLocation)

        # Sort Rider-Name Sheet by last updated so that accounts most in need of update can be updated first.
        # instaloader has a limit of about 100 accounts per day, so there is a limit as to how up to date the data is (of about 7-10 days)
        sortRiderSheetByLastIgFollowerUpdate(googleSheetObject)

        # Create a list of ig accounts you want the number of followers of
        igAccounts = getIgAccountNames(googleSheetObject)

        #Get the index for todays column
        todaysColIndex = getTodaysColumnIndex(googleSheetObject)

        # Set todays date in header row
        setMasterSheetDateHeader(googleSheetObject, todaysColIndex)


        # Set a value in the sheet
        setFollowerCountFromListPos(listIndex=0, colIndex=todaysColIndex, sheetObject=googleSheetObject, followerCount = 500)




main()