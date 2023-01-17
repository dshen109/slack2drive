import os

import requests


PHOTO_TYPES = ('jpg', 'gif', 'heic', 'png', 'raw')


def fileinfo(trigger):
    files = trigger['event'].get('files')
    if not files:
        return []
    else:
        return files


def download(file_payload, token):
    filetype = file_payload['filetype']
    if filetype not in PHOTO_TYPES:
        return None

    url = file_payload['url_private_download']
    filename = file_payload['name']
    r = requests.get(url, headers={'Authorization': 'Bearer %s' % token})
    r.raise_for_status
    file_data = r.content   # get binary content
    with open(os.path.join('/tmp', filename) , 'w+b') as f:
        f.write(bytearray(file_data))
    return filename


def handler(pd: 'pipedream'):
    files = fileinfo(pd.steps['trigger'])

    if not files:
        pd.flow.exit("No files in message.")

    token = pd.inputs["slack"]["$auth"]["oauth_access_token"]

    downloaded = []
    for file in files:
        fname = download(file, token)
        if fname:
            downloaded.append(fname)

    if not downloaded:
        pd.flow.exit("No image files in message.")

    return {'files': downloaded}
