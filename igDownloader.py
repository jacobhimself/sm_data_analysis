"""
Author: Jacob France
Date: 30/11/2023
File Description:
To collect instagram follower data and export it to a Google Drive folder. 
A Google Apps Script will handle the uploading of that data to a Google Sheet for data analysis
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

import os.path
from datetime import date
import instaloader
import time

from googleSheetsHelper import *

sharedFolderId = "1LrkxznfjcjB2Gmg180FdPF0U3JHyBV-Z"
scope = 'https://www.googleapis.com/auth/drive'
keyFileLocation = os.path.dirname(os.path.realpath(__file__)) + '/cloud_service_account_key.json'
dateAsString = str(date.today())


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

def retrieveIgFollowers(igSession):
    # Get the Google Sheet Object
    googleSheetObject = getGoogleSheet(sheetsApi, sheetsApiVersion, [], keyFileLocation)

    # Sort Rider-Name Sheet by last updated so that accounts most in need of update can be updated first.
    # instaloader has a limit of about 100 accounts per day, so there is a limit as to how up to date the data is (of about 7-10 days)
    sortRiderSheetByLastIgFollowerUpdate(googleSheetObject)

    # Create a list of ig accounts you want the number of followers of
    igAccounts = getIgAccountNamesFromRiderSheet(googleSheetObject)

    #Get the index for todays column
    todaysColIndex = getTodaysColumnIndex(googleSheetObject)

    # Set todays date in header row
    setMasterSheetDateHeader(googleSheetObject, todaysColIndex)

    # Get list of handle names from Master Sheet
    # Master sheet is not in same order as Riders sheet so we need to 
    # find the row index of each record
    masterSheetHandles = getIgAccountNamesFromMasterSheet(googleSheetObject)

    print("There are " + str(len(igAccounts)) + " accounts to get followers for")
    count = 0
    print(igAccounts)

    for handle in igAccounts:
        dl_user = handle[0]
        print("Gathering data for ", dl_user)
        todaysFollowerCount = instaloader.Profile.from_username(igSession.context, dl_user).followers
        print("follower count for " + dl_user + " is " + str(todaysFollowerCount))
        masterSheetIndex = masterSheetHandles.index([dl_user])
        print("found " + dl_user + " in masterSheet")
        
        setFollowerCountFromListPos(listIndex=masterSheetIndex, colIndex=todaysColIndex, sheetObject=googleSheetObject, followerCount=todaysFollowerCount)
        setlastIgFollowerUpdate(listIndex=count, sheetObject=googleSheetObject)
        print("Finished data gathering for " + dl_user)
        time.sleep(30)
        count += 1


def main():

    # Load the instaloader session from file
    try:
        newLoader = loadIgSession()

    except Exception as e:
        print(f'An error occurred while using the instaloader module or writing to output csv file: {e}')

    # Loop through instagram handles and add follower counts to Google Sheet
    retrieveIgFollowers(newLoader)
    
main()
