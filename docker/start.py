import sys
import os
import shutil

def run(command):
    if os.system(command) is not 0:
        raise Exception('Error! "%s" returned non-zero error code' % command)

# Get latest version
print '\nPulling latest version...\n'
os.chdir('/srv/hcc-photo-upload')
run('git fetch origin')
if len(sys.argv) > 1:
    print '\nPulling branch %s\n' % sys.argv[1]
    if os.system('git show-ref --verify --quiet refs/heads/%s' % sys.argv[1]) is not 0:
        # If this branch doesn't exist locally, add a remote
        run('git checkout --track origin/%s' % sys.argv[1])
run('python /srv/hcc-photo-upload/setup.py develop')

# Set up database
print '\nInitializing default database using init script...\n'
run('initialize_hcc-photo-upload_db /srv/hcc-photo-upload/production.ini')
print '\nDone initializing database.\n'

# Start system
print '\nStarting supervisor...\n'
os.system('supervisord -n')
