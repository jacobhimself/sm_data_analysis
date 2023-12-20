from googleapiclient.discovery import build
from google.oauth2 import service_account
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