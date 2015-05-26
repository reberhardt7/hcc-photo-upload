import os
import magic
import transaction
import shutil
import logging
from pyramid.view import view_config
from pyramid.response import Response, FileResponse
from datetime import datetime
from models import DBSession, Photo, GDriveAccount
from oauth2client.client import OAuth2WebServerFlow
from pyramid.httpexceptions import HTTPFound

log = logging.getLogger(__name__)

# Google Drive oauth
CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'


def error_response(code, msg):
    status = {400: '400 Bad Request', 500: '500 Internal Server Error'}[code]
    resp = Response(msg)
    resp.status_code = code
    resp.status_string = status
    return resp

@view_config(route_name='home')
def home(request):
    return FileResponse(os.path.join(os.path.dirname(__file__), 'static', 'index.html'), request=request)

@view_config(route_name='upload')
def upload(request):
    if request.content_length/1000000 > 20:
        return error_response(400, 'Sorry, but the file must be under 20MB.')

    # Create photo object in database
    photo = Photo(datetime.today(), request.POST['file'].filename, request.client_addr, request.content_type, request.content_length)
    DBSession.add(photo)
    DBSession.flush()

    # Save uploaded file
    input_file = request.POST['file'].file
    input_file.seek(0)
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists('data/uploads'):
        os.makedirs('data/uploads')
    upload_path = os.path.join('data', 'uploads', str(photo.id))
    with open(upload_path, 'w') as f:
        shutil.copyfileobj(input_file, f)

    # Check the content type and rename as appropriate
    mime = magic.from_file(upload_path, mime=True)
    if mime not in ['image/jpeg', 'image/pjpeg', 'image/gif', 'image/png', 'image/tiff', 'image/x-tiff']:
        resp = Response('Sorry, but we can only accept jpg, gif, or png files.')
        resp.status_code = 400
        resp.status_string = '400 Bad Request'
        return resp
    extension = {'image/jpeg': '.jpg', 'image/pjpeg': '.jpg',
                 'image/gif': '.gif', 'image/png': '.png',
                 'image/tiff': '.tiff', 'image/x-tiff': '.tiff'}[mime]
    os.rename(upload_path, upload_path + extension)
    photo.content_type = mime

    return Response('OK')

@view_config(route_name='authorize_gdrive')
def authorize_gdrive(request):
    log.info('authorize_gdrive called at %s', request.url)

    # Check to make sure we haven't already been linked to another account
    if DBSession.query(GDriveAccount).count():
        log.error('The uploader has already been linked to a Google account.')
        return error_response(400, 'The uploader has already been linked to a Google account.')

    # Go through the authorization flow to get an auth token
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE,
                               redirect_uri=request.route_url('oauth2callback'))
    flow.params['access_type'] = 'offline'
    flow.params['approval_prompt'] = 'force'
    authorize_url = flow.step1_get_authorize_url()
    log.info('Redirecting user to %s', authorize_url)
    return HTTPFound(authorize_url)

@view_config(route_name='oauth2callback')
def oauth2callback(request):
    log.info('oauth2callback called at %s', request.url)

    # Get the auth code from the GET params
    try:
        code = request.GET['code']
        log.info('Successfully got auth code')
    except KeyError:
        log.error('Could not find auth code in GET params')
        return error_response(500, 'Sorry, but Google authorization failed.')

    # Exchange the auth code for a bearer/access token
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE,
                               redirect_uri=request.route_url('oauth2callback'))
    credentials = flow.step2_exchange(code)
    try:
        access_token = credentials.access_token
        refresh_token = credentials.refresh_token
        token_expiry = credentials.token_expiry
        if access_token is None or refresh_token is None or token_expiry is None:
            raise ValueError
    except (AttributeError, ValueError):
        log.error('Could not get access token, refresh token, and/or token expiry from exchanged credentials')
        return error_response(500, 'Sorry, but Google authorization failed.')
    DBSession.add(GDriveAccount(access_token, refresh_token, token_expiry))

    return Response('Successfully authorized with Google Drive!')
