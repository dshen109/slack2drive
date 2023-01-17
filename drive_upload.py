import os

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


def handler(pd: 'pipedream'):
    files = pd.steps['slack']['$return_value']['files']
    token = pd.inputs['google_drive']['$auth']


    credentials = Credentials(
        token['oauth_access_token'],
        refresh_token=token['oauth_refresh_token'],
        client_id=token['oauth_client_id']
    )

    payload = {
        'result': []
    }

    with build('drive', 'v3', credentials=credentials) as service:
        for filename in files:
            media =  MediaFileUpload(
                os.path.join('/tmp', filename),
                chunksize=1024*1024, resumable=True
            )

            file_metadata = {
                'name': filename,
                'parents': [os.environ.get('GDRIVE_PARENT')]
            }
            file = service.files().create(
                body=file_metadata, media_body=media,
                fields='id').execute()
            print(f"Uploaded {filename} with ID {file.get('id')}")
            payload['result'].append(
                {'filename': filename, 'id': file.get('id')}
            )
    return payload
