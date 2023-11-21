# import numpy as np
import csv
from datetime import date
import instaloader

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








