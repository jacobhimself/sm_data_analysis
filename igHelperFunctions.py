# import numpy as np
import csv
from datetime import date
import instaloader
import time

def createIgSession(userName, password):
    session = instaloader.Instaloader()
    session.login(userName,password)
    return session

#Given a csv file of instagram handles, return a dictionary with all keys set to -1
def populateDefaultDict(igHandleCSV_filename):
    tempDict = {}
    with open(igHandleCSV_filename, 'r') as f:
    #remove line break and add key:value pair to dictionary
        for line in f:
            tempDict[line.strip()] = -1
    f.close()
    return tempDict

#Given a dict with instagram handles as keys, populate the values from instagram
def populateFollowerDict(handleDictIn, igSession):
    for handle in handleDictIn.keys():
        dl_user = handle
        print("Gathering data for ", dl_user)
        handleDictIn[handle] = instaloader.Profile.from_username(igSession.context, dl_user).followers
        # going to try without return incase handleDictIn is global?

# ADD CONTENTS OF RIDER : FOLLOWER DICT TO TODAYS_DATE.CSV
def saveDictToCSV(dictIn):
    dateAsString = str(date.today())
    outputFileName = dateAsString + ".csv"

    with open(outputFileName,'w') as f:
        w = csv.writer(f)
        w.writerows(dictIn.items())
    
    print("The following key:value pairs have been saved to csv")
    for x, y in dictIn.items():
        print(x, y)


#Given a dict with instagram handles as keys, create a new dict where the values
# represent the number of times each account is followed by an account in the original dict
def updateHandlesTracked(handleDictIn, igSession):
    originalHandleKeys = list(handleDictIn.keys())
    newHandleDict = handleDictIn.copy()
    for handle in originalHandleKeys:
        dl_user = handle
        print("Gathering accounts followed by ", dl_user)
        tempFollowees = instaloader.Profile.from_username(igSession.context, dl_user).get_followees()

        for followee in tempFollowees:
            checkHandle = followee.username
            print(checkHandle)
            if(checkHandle in newHandleDict):
                newHandleDict[checkHandle] += 1
            else:
                newHandleDict[checkHandle]  = 1
        print("Followers for " + dl_user + " added to new list")
        time.sleep(30)
    return newHandleDict

# Create a csv file containing all the new accounts
def saveUpdatedHandleDictToCSV(dictIn):
    dateAsString = str(date.today())
    outputFileName = "updatedHandleList: " + dateAsString + ".csv"

    with open(outputFileName,'w') as f:
        w = csv.writer(f)
        w.writerows(dictIn.items())
    
    print("The following key:value pairs have been saved to csv")
    for x, y in dictIn.items():
        print(x, y)

# Loop through all riders currently tracked, and add the
# accounts they follow to a list
def getNewRiderList():

    dateAsString = str(date.today())
    handleFileName = "Handles: " + dateAsString + ".csv"
    handleFileNamePath = "handle_files/" + handleFileName 
    USER = "jefethesecond"
    SESSIONFILE = "session-jefethesecond"
    L = instaloader.Instaloader()

    L.load_session_from_file(USER, SESSIONFILE)

    currentlyFollowed = populateDefaultDict(handleFileNamePath)

    updatedHandlesTracked = updateHandlesTracked(currentlyFollowed, L)

    saveUpdatedHandleDictToCSV(updatedHandlesTracked)








