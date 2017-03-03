# tell docker which basic image my new image is based on
FROM centos:7

# get anaconda
#FROM continuumio/anaconda

# install packages
RUN yum -y install epel-release \ 
        && yum -y install nginx python-pip supervisor uwsgi-plugin-python git\
	&& yum -y update \
	&& yum -y clean all

RUN git clone https://github.com/ytsapras/robonet_site

# will open port 80 for the webserver to be run on
EXPOSE 80

# install requirements
COPY requirements.txt /var/www/html/
RUN pip install -r /var/www/html/requirements.txt \
    && rm -rf ~/.cache ~/.pip

COPY init init/
COPY mycode /var/www/html/


ENTRYPOINT["/init"]
CMD /bin/tcsh
