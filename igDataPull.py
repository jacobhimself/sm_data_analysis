from igHelperFunctions import *

# Set username and password for instagram (ig) session before creating
# an object for said session
USER = "freshaccount4jefe"
PASSWORD = "TESTACCOUNT4321"
igSession = createIgSession(USER,PASSWORD)

# Import csv list of ig account handles and create default dict to store them
csvAccountList = "ighandles.csv"
followerDict = populateDefaultDict(csvAccountList)

# Populate follower dict with actual follower counts
populateFollowerDict(followerDict, igSession)

saveDictToCSV(followerDict)




# dl_user = "wattzup"

# profile = instaloader.Profile.from_username(igSession.context, dl_user)


# Code below could potentially be helpful for future use??
    # L.login(USER, "TESTACCOUNT4321")

    # # Load session previously saved with `instaloader -l USERNAME`:
    # # L.load_session_from_file(USER)