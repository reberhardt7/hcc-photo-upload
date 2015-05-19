#! /bin/bash

# Updates site to latest version
cd /srv/hcc-photo-upload
git pull
python /srv/hcc-photo-upload/setup.py develop
uwsgi --reload /srv/hcc.pid
