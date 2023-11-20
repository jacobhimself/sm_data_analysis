# import numpy as np
import csv
from datetime import date


#Given a csv file of instagram handles, return a dictionary with all keys set to -1
def populateDict(igHandleCSV):
    tempDict = {}
    with open(igHandleCSV, 'r') as f:
    #remove line break and add key:value pair to dictionary
        for line in f:
            tempDict[line.strip()] = -1
    f.close()
    return tempDict


# ADD CONTENTS OF RIDER : FOLLOWER DICT TO TODAYS_DATE.CSV
def saveDictToCSV(dictIn):
    datetimeAsString = str(date.today())
    outputFileName = datetimeAsString + ".csv"

    with open(outputFileName,'w') as f:
        w = csv.writer(f)
        w.writerows(dictIn.items())
    
    for x, y in rider_dict.items():
        print(x, y)




# test the functions
rider_dict = populateDict("ighandles.csv")
saveDictToCSV(rider_dict)









