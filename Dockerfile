# tell docker which basic image my new image is based on
FROM centos:7

# will open port 80 for the webserver to be run on
EXPOSE 80
ENTRYPOINT ["/init"]

# install packages
RUN yum -y install epel-release \ 
        && yum -y install nginx python-pip supervisor uwsgi-plugin-python MySQL-python tkinter wget\
	&& yum -y update \
	&& yum -y clean all

# install Python requirements
COPY requirements.txt /var/www/html/
RUN pip install --upgrade pip
RUN pip install -r /var/www/html/requirements.txt \
    && rm -rf ~/.cache ~/.pip

# Install sextractor under /usr/bin/sex
ENV SEX_PKG sextractor-2.19.5-1.x86_64.rpm
RUN curl -q -O http://www.astromatic.net/download/sextractor/$SEX_PKG && \
    rpm --install --quiet $SEX_PKG 

# Install sewpy
RUN git clone https://github.com/megalut/sewpy/ sewpy/
RUN cd sewpy/
RUN python setup.py install
RUN cd ..
RUN rm -rf sewpy/

# operating system configuration
COPY docker/ /

COPY . /var/www/robonetsite/
