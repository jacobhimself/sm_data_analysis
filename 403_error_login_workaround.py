"""
Script is downloaded from instaloader github - https://instaloader.github.io/troubleshooting.html#login-error
It creates a session file from a browser based session on Firefox, allowing the bypass of the normal login procedure

I ran the script slightly different to how instaloader suggests.
1: Log in to instagram on Firefox
2: Retrieve the cookie file. In my version of Ubuntu this was stored in /home/jacob/snap/firefox/common/.mozilla/firefox/70luzall.default/cookies.sqlite
3: Store the cookie file in the same folder as this script
4. I have added the additional filepath for Ubuntu to the get_cookiefile function
5: Run the file with the terminal command: python3 615_import_firefox_session.py -c cookies.sqlite
6: This creates a session file that can then be loaded by instaloader. For me the file was in /home/jacob/.config/instaloader
7: Then in the actual instaloader script, use the following code
    USER = "your_account_name_here"
    L = instaloader.Instaloader()
    L.load_session_from_file(USER, "your_session_file_name_here")





"""

from argparse import ArgumentParser
from glob import glob
from os.path import expanduser
from platform import system
from sqlite3 import OperationalError, connect

try:
    from instaloader import ConnectionException, Instaloader
except ModuleNotFoundError:
    raise SystemExit("Instaloader not found.\n  pip install [--user] instaloader")


def get_cookiefile():
    default_cookiefile = {
        "Windows": "~/AppData/Roaming/Mozilla/Firefox/Profiles/*/cookies.sqlite",
        "Darwin": "~/Library/Application Support/Firefox/Profiles/*/cookies.sqlite",
        "Ubuntu": "cookies.sqlite"
    }.get(system(), "~/.mozilla/firefox/*/cookies.sqlite")
    cookiefiles = glob(expanduser(default_cookiefile))
    if not cookiefiles:
        raise SystemExit("No Firefox cookies.sqlite file found. Use -c COOKIEFILE.")
    return cookiefiles[0]


def import_session(cookiefile, sessionfile):
    print("Using cookies from {}.".format(cookiefile))
    conn = connect(f"file:{cookiefile}?immutable=1", uri=True)
    try:
        cookie_data = conn.execute(
            "SELECT name, value FROM moz_cookies WHERE baseDomain='instagram.com'"
        )
    except OperationalError:
        cookie_data = conn.execute(
            "SELECT name, value FROM moz_cookies WHERE host LIKE '%instagram.com'"
        )
    instaloader = Instaloader(max_connection_attempts=1)
    instaloader.context._session.cookies.update(cookie_data)
    username = instaloader.test_login()
    if not username:
        raise SystemExit("Not logged in. Are you logged in successfully in Firefox?")
    print("Imported session cookie for {}.".format(username))
    instaloader.context.username = username
    instaloader.save_session_to_file(sessionfile)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("-c", "--cookiefile")
    p.add_argument("-f", "--sessionfile")
    args = p.parse_args()
    try:
        import_session(args.cookiefile or get_cookiefile(), args.sessionfile)
    except (ConnectionException, OperationalError) as e:
        raise SystemExit("Cookie import failed: {}".format(e))