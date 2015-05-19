import os
import magic
import transaction
import shutil
from pyramid.view import view_config
from pyramid.response import Response, FileResponse
from datetime import datetime
from models import DBSession, Photo


@view_config(route_name='home')
def home(request):
    return FileResponse(os.path.join(os.path.dirname(__file__), 'static', 'index.html'), request=request)

@view_config(route_name='upload')
def upload(request):
    if request.content_length/1000000 > 20:
        resp = Response('Sorry, but the file must be under 20MB.')
        resp.status_code = 400
        resp.status_string = '400 Bad Request'
        return resp

    # Create photo object in database
    photo = Photo(datetime.today(), request.POST['file'].filename, request.client_addr, request.content_type, request.content_length)
    DBSession.add(photo)
    DBSession.flush()

    # Save uploaded file
    input_file = request.POST['file'].file
    input_file.seek(0)
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    upload_path = os.path.join('uploads', str(photo.id))
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
