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
import csv
from datetime import date
import instaloader
import time

sharedFolderId = "1LrkxznfjcjB2Gmg180FdPF0U3JHyBV-Z"
scope = 'https://www.googleapis.com/auth/drive'
keyFileLocation = os.path.dirname(os.path.realpath(__file__)) + '/cloud_service_account_key.json'
dateAsString = str(date.today())
handleFileName = "Handles: " + dateAsString + ".csv"
handleFileNamePath =  os.path.dirname(os.path.realpath(__file__)) +  "/handle_files/" + handleFileName 
outputCsvFileName = dateAsString + ".csv"
outputCsvFileNamePath = os.path.dirname(os.path.realpath(__file__))+ "/follower_files/" + outputCsvFileName


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

# Retrieve csv ig handle list from Drive and save in handle_files/"todaysFile"
def downloadHandleList(serviceObject):
    #search for the file by name
    results = serviceObject.files().list(q=f"name='{handleFileName}'").execute()
    files = results.get('files',[])


    if not files:
        print(f"No file with the name '{handleFileName}' found.")
    else:
        file_id = files[0]['id']
    
    #download the csv file and save/write it to the handle_files folder
    request = serviceObject.files().get_media(fileId = file_id)
    with open(handleFileNamePath, 'wb') as file:
        file.write(request.execute())
        print(f"CSV file '{handleFileName}' downloaded to '{handleFileNamePath}'.")

# Use instaloader module to retrieve follower data, save the data in follower_files/"todaysFile"
def ig_data_pull():
    # Retrieve existing session so that Instagram IP address check is bypassed
    # If Instagram suspects suspicious activity, they will require a manual verification
    # A new session can be created with the createIGSession function, and Instaloader.save_session(), which creates the dict in the sessionDict variable below
    USER = "freshaccount4jefe"

    try:
        loader = instaloader.Instaloader() 
        sessionDict = {'csrftoken': '8oMqJquDoM6S8UbMMOwUswTv2SIPLYOP', 'ds_user_id': '62843338333', 'ig_cb': '1', 'ig_did': 'EAD711BE-5F4E-4262-ACF1-D65CB4FC15AA', 'ig_pr': '1', 'ig_vw': '1920', 'mid': 'ZWaQ4AAEAAE-hHODqUdpDkrKtwBj', 'rur': '"EAG\\05462843338333\\0541732756579:01f7a9515a87e7fc4728300da6140e407af968673e431f124e189a108a268326aa9ae5ff"', 's_network': '', 'sessionid': '62843338333%3A2MF68v4jAHiZX6%3A17%3AAYdji0eODACxtkakspjtlHhI_UuO1nAai-SNcGeM2g'}
        loader.load_session(USER,sessionDict)
    
    except Exception as e:
        print(f'An error occurred while loading instaloader session: {e}')


    # Import csv list of ig account handles and create default dict to store them
    followerDict = populateDefaultDict()

    # Populate follower dict with actual follower counts
    populateFollowerDict(followerDict, loader)

    # Write the follower dict to file
    saveDictToCSV(followerDict)

# Create a dict with a key for each handle in the handle_files/"todaysFile" csv, and the value set to -1
# This is to help easily identify any missing values
def populateDefaultDict():

    tempDict = {}
    with open(handleFileNamePath, 'r') as f:

        #remove line break and add key:value pair to dictionary
        for line in f:
            tempDict[line.strip()] = -1
    f.close()
    return tempDict

# Given a dict with instagram handles as keys, populate the values from instagram
# time.sleep(30) is used to stop instaloader from triggering Instagram's suspicious activity check by slowing down requests to 2 per minute
def populateFollowerDict(handleDictIn, igSession):
    count = 0
    for handle in handleDictIn.keys():
        dl_user = handle
        print("Gathering data for ", dl_user)
        handleDictIn[handle] = instaloader.Profile.from_username(igSession.context, dl_user).followers
        time.sleep(30)
        count += 1

# Write contents of handle : follower dict to follower_files/"todaysFile"
def saveDictToCSV(dictIn):

    with open(outputCsvFileNamePath,'w') as f:
        w = csv.writer(f)
        w.writerows(dictIn.items())
    
    print("The following key:value pairs have been saved to csv")
    for x, y in dictIn.items():
        print(x, y)

# Upload the completed handle,follower csv file to Google Drive
def uploadCsvFile(serviceObject):

    file_metadata = {"name": outputCsvFileName, "parents":[sharedFolderId]}
    media = MediaFileUpload(outputCsvFileNamePath, mimetype="text/csv", resumable=True)
    file = (
        serviceObject.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

# In the event that a new IgSession needs creating, use this function and the Instaloader.save_session() method (to get the session instance)
# def createIgSession(userName, password):
#     session = instaloader.Instaloader()
#     session.login(userName,password)
#     return session

def main():

    # Create a service object, "service" that represents our Google Drive
    # Methods can then be used to perform certain functions to download or upload data
    try:
        # Authenticate and construct service.
        service = getMyDrive(api_name='drive', api_version='v3', scopes=[scope], key_file_location=keyFileLocation)
        
    except HttpError as error:
        print(f'An error occurred: {error}')


    # Download the list of instagram handles to check for the current day
    try:
        downloadHandleList(service)

    except Exception as e:
        print(f'An error occurred while downloading handles from Google Drive API: {e}')

    
    # Use the instaloader module to populate the csv file containing both handles and follower counts
    try:
        ig_data_pull()

    except Exception as e:
        print(f'An error occurred while using the instaloader module or writing to output csv file: {e}')


    # Upload the completed handle-follower count csv file to the Google Drive
    try:
        uploadCsvFile(service)

    except Exception as e:
        print(f'An error occurred while uploading handle-follower csv file to Google Drive API: {e}')
    


main()
