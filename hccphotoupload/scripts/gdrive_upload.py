import httplib2
import pprint
import sys
import os
import logging
import re
import transaction

from time import sleep

from sqlalchemy import engine_from_config

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from hccphotoupload.models import (
    Photo,
    GDriveAccount,
    )

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from apiclient import errors
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import OAuth2Credentials

log = logging.getLogger(__name__)

CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']

OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

TARGET_FOLDERNAME = os.environ['GOOGLE_TARGET_FOLDERNAME']

drive_service = None


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def upload_photos():
    global drive_service

    if not drive_service and not DBSession.query(GDriveAccount).count():
        log.info('No Google Drive account has been authorized yet.')
    elif not drive_service:
        # The drive service hasn't been set up, but a Google account is ready to use
        # Get oauth info from db and set up service
        log.info('Setting up Google OAuth service')
        authorized_user = DBSession.query(GDriveAccount).first()
        access_token = authorized_user.access_token
        refresh_token = authorized_user.refresh_token
        token_expiry = authorized_user.token_expiry
        credentials = OAuth2Credentials(access_token, CLIENT_ID, CLIENT_SECRET,
                                        refresh_token, token_expiry,
                                        token_uri='https://accounts.google.com/o/oauth2/token',
                                        user_agent=None)
        http = httplib2.Http()
        http = credentials.authorize(http)
        drive_service = build('drive', 'v2', http=http)

    if drive_service:
        # Upload them photos
        log.info('Uploading photos to Google Drive')
        toUpload = DBSession.query(Photo).filter(Photo.uploaded_to_gdrive==False).all()
        log.info('Uploading {}'.format(toUpload))
        try:
            parent_folder = [f for f in drive_service.files().list(q="title = '{}'".format(TARGET_FOLDERNAME)).execute()['items'] if not f['labels']['trashed'] and f['parents'][0]['isRoot']]
            if not parent_folder:
                log.info('Creating new folder "{}"'.format(TARGET_FOLDERNAME))
                parent_folder = drive_service.files().insert(body={'title': TARGET_FOLDERNAME, 'mimeType': 'application/vnd.google-apps.folder'}).execute()
            else:
                parent_folder = parent_folder[0]
            
            for photo in toUpload:
                extension = {'image/jpeg': '.jpg', 'image/pjpeg': '.jpg',
                             'image/gif': '.gif', 'image/png': '.png',
                             'image/tiff': '.tiff', 'image/x-tiff': '.tiff'}[photo.content_type]
                media_body = MediaFileUpload(os.path.join('data', 'uploads', str(photo.id) + extension), mimetype=photo.content_type, resumable=True)
                body = {
                  'title': '{}-{}{}'.format(photo.id, re.sub(r'[^\w\d\-_]', '_', photo.original_filename.rsplit('.', 1)[0]), extension),
                  'description': '{} uploaded by {} on {}'.format(photo.original_filename, photo.uploader_ip, photo.date_uploaded.strftime('%B %d, %Y %I:%M:%S %p')),
                  'mimeType': photo.content_type,
                  'parents': [{'id': parent_folder['id']}]
                }
                log.info('Uploading {}: {}'.format(photo.id, body))
                drive_service.files().insert(body=body, media_body=media_body).execute()
                with transaction.manager:
                    photo.uploaded_to_gdrive = True
                    DBSession.add(photo)
                os.remove(os.path.join('data', 'uploads', str(photo.id) + extension))

            orphaned_files = [f for f in os.listdir('data', 'uploads') if not f.startswith('.')]
            if orphaned_files:
                log.warn('Warning: The following uploaded files have been orphaned in the database: %s' % orphaned_files)

        except errors.HttpError, e:
            if e.resp.status == 401:
                log.error('Error connecting to Google Drive! The user has been de-authorized.')
                sys.exit(-1)
            else:
                raise
                #TODO: Log instead of raising, because this will terminate the upload loop

def main():
    # Bind database using config file
    if len(sys.argv) < 2:
        usage(sys.argv)
    config_uri = sys.argv[1]
    options = parse_vars(sys.argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    global DBSession
    DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), expire_on_commit=False))
    DBSession.configure(bind=engine)

    while True:
        upload_photos()
        sleep(60)

if __name__ == '__main__':
    main()
