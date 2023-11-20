import instaloader
from datetime import datetime

L = instaloader.Instaloader()

# bot = instaloader.Instaloader()

# profile = Profile.from_username(L.context, 'wattzup/')

# print(type(profile))





USER = "freshaccount4jefe"
# PROFILE = USER

L.login(USER, "TESTACCOUNT4321")

# # Load session previously saved with `instaloader -l USERNAME`:
# # L.load_session_from_file(USER)

# profile = instaloader.Profile.from_username(L.context, "nekleveljacob.co.nz")


# print("Fetching followers of profile {}.".format(profile.username))
# followers = set(profile.get_followers())

# for i in followers:
#     print(i)


# username = "nekleveljacob.co.nz"

# myProfile = instaloader.Profile.from_username(L.context, username)

# myProfile.

dl_user = "wattzup"

# L.download_profile(dl_user, )

profile = instaloader.Profile.from_username(L.context, dl_user)


print(profile.followers)