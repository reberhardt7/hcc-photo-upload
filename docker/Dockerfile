# Base image ubuntu
FROM ubuntu

MAINTAINER Ryan Eberhardt <reberhardt7@gmail.com>

# Update apt repositories
RUN apt-get update

# Install editors
RUN apt-get install -y vim
RUN apt-get install -y nano

# Install basic requirements
RUN apt-get install -y build-essential python-dev supervisor nginx uwsgi uwsgi-plugin-python python-setuptools libmagic-dev git
RUN easy_install virtualenv uwsgi pyramid distribute

# Set system time
RUN echo 'America/Chicago' > /etc/timezone
RUN dpkg-reconfigure --frontend noninteractive tzdata

# Configure nginx
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
ADD hcc.conf /etc/nginx/conf.d/hcc.conf
RUN rm /etc/nginx/sites-enabled/default
RUN mkdir -p /var/log/nginx/hcc
RUN groupadd uwsgi
RUN useradd uwsgi -g uwsgi

# Open incoming ports
EXPOSE 80

# Add supervisord configuration files
ADD supervisor_config/nginx.conf /etc/supervisor/conf.d/nginx.conf
ADD supervisor_config/hcc.conf /etc/supervisor/conf.d/hcc.conf
ADD supervisor_config/hcc-gdrive.conf /etc/supervisor/conf.d/hcc-gdrive.conf

# Set up Python/Pyramid environment
RUN mkdir -p /srv

# Set up site
RUN git clone -b master https://github.com/reberhardt7/hcc-photo-upload.git /srv/hcc-photo-upload
RUN python /srv/hcc-photo-upload/setup.py develop
ADD update.sh /srv/update.sh
RUN chmod +x /srv/update.sh
RUN touch /srv/uwsgi.log
RUN mkdir /srv/hcc-photo-upload/uploads
RUN chown -R uwsgi /srv/hcc-photo-upload /srv/uwsgi.log

# Run supervisor
ADD start.py /start.py
CMD ["master"]
ENTRYPOINT ["python", "/start.py"]

# Build instructions:
# This file must be named Dockerfile.  CD to its parent directory, then:
# docker build -t="hcc/hcc-photo-upload" .

# To run the built image (maps port 80 on host to 80 of container):
# docker run -d -p 80:80 hcc/hcc-photo-upload
# To use a data directory:
# docker run -d -v /home/user/hcc-photos:/srv/hcc-photo-upload/uploads hcc/hcc-photo-upload
