# tell docker which basic image my new image is based on
FROM centos:7

# get anaconda
#FROM continuumio/anaconda

# install packages
RUN yum -y install epel-release \ 
        && yum -y install nginx python-pip supervisor uwsgi-plugin-python git \
	&& yum -y install python-dev python-devel freetype freetype-devel libpng-devel \
	&& yum -y install kernel-devel gcc gcc-c++ \
	&& yum -y update \
	&& yum -y clean all

RUN git clone https://github.com/ytsapras/robonet_site

# will open port 80 for the webserver to be run on
EXPOSE 80
ENTRYPOINT ["/init"]

# install requirements
COPY requirements.txt /var/www/html/
RUN pip install -r /var/www/html/requirements.txt \
    && rm -rf ~/.cache ~/.pip


COPY robonet_site /var/www/html/.

