# tell docker which basic image my new image is based on
FROM centos:7

# will open port 80 for the webserver to be run on
EXPOSE 80
ENTRYPOINT ["/init"]

# Establish user ID of container while running
RUN groupadd -g 20000 domainusers \
    && useradd -u 20007 -g 20000 -c "Microlensing user" -d /home/robouser -s /bin/bash robouser

# install packages
RUN yum -y install epel-release \ 
        && yum -y install nginx python-pip supervisor python-devel git \
	&& yum -y install uwsgi-plugin-python2 MySQL-python tkinter wget gcc g++ gcc-gfortran\
	&& yum -y update  \
	&& yum -y clean all

# install Python requirements
COPY requirements.txt /var/www/html/
RUN pip install --upgrade pip \
    && pip install numpy \
    && pip install pytest \
    && pip install -r /var/www/html/requirements.txt \
    && rm -rf ~/.cache ~/.pip

# Install sextractor under /usr/bin/sex
ENV SEX_PKG sextractor-2.19.5-1.x86_64.rpm
RUN curl -q -O http://www.astromatic.net/download/sextractor/$SEX_PKG && \
    rpm --install --quiet $SEX_PKG 

# Install sewpy
RUN git clone https://github.com/megalut/sewpy/ && cd sewpy/ && python setup.py install && cd .. && rm -rf sewpy/

# operating system configuration
COPY docker/ /

COPY . /var/www/robonetsite/
