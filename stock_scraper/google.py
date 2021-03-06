import argparse
import json
import os
import os.path

import httplib2
from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'STOCKS'
SHEET_ID = '10sHdXR_NyQ-hxrEu7QALDX5qwuLWjCAfENSh2c3Cka4'
CREDENTIALS = 'sheets.googleapis.com-python-quickstart.json'
CREDENTIALS_DIR = '.credentials'


def create_secrets_file():
    """
    We can't commit the secrets file to the repo but google's
    oauth2client must read the secrets from the secrets json
    file.

    So we read all the secrets from ENV variables and recreate
    the JSON file.
    """
    if os.path.isfile(CLIENT_SECRET_FILE):
        return

    secret_json = {
        'installed': {
            'client_id': os.environ['GOOGLE_OAUTH_CLIENT_ID'],
            'project_id': os.environ['GOOGLE_OAUTH_PROJECT_ID'],
            'auth_uri': os.environ['GOOGLE_OAUTH_AUTH_URI'],
            'token_uri': os.environ['GOOGLE_OAUTH_TOKEN_URI'],
            'auth_provider_x509_cert_url': os.environ['GOOGLE_OAUTH_PROVIDER'],
            'client_secret': os.environ['GOOGLE_OAUTH_CLIENT_SECRET'],
            'redirect_uris': os.environ['GOOGLE_OAUTH_REDIRECT_URIS'],
        }
    }

    with open(CLIENT_SECRET_FILE, 'w') as fp:
        json.dump(secret_json, fp)


class SheetService:
    def __init__(self, home_dir, flags):
        self.http = httplib2.Http()
        self.home_dir = home_dir
        self.service = self.get_service(flags)

    def get_values(self, range):
        """"""
        return self.service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range=range).execute()

    def get_and_update(self, query):
        body = {'valueInputOption': 'USER_ENTERED', 'data': query}
        return self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=SHEET_ID, body=body).execute()

    def get_credentials(self, flags):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        credential_dir = os.path.join(self.home_dir, CREDENTIALS_DIR)
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, CREDENTIALS)
        create_secrets_file()

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            secrets_file = os.path.join(self.home_dir, CLIENT_SECRET_FILE)
            flow = client.flow_from_clientsecrets(secrets_file, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                flags_args = argparse.ArgumentParser(
                    parents=[tools.argparser]).parse_args([flags])
                credentials = tools.run_flow(flow, store, flags_args)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def get_service(self, flags):
        credentials = self.get_credentials(flags)
        http = credentials.authorize(self.http)
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build(
            'sheets',
            'v4',
            http=http,
            discoveryServiceUrl=discoveryUrl,
            cache_discovery=False)
        return service
