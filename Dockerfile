# tell docker which basic image my new image is based on
FROM centos:7

# will open port 80 for the webserver to be run on
EXPOSE 80
ENTRYPOINT ["/init"]

# install packages
RUN yum -y install epel-release \ 
        && yum -y install nginx python-pip supervisor uwsgi-plugin-python MySQL-python \
	&& yum -y update \
	&& yum -y clean all

# install requirements
COPY requirements.txt /var/www/html/
RUN pip install -r /var/www/html/requirements.txt \
    && rm -rf ~/.cache ~/.pip

COPY . /var/www/robonetsite/
