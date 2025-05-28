FROM python:3.12

COPY dependencies.txt /dependencies.txt
RUN pip install -r dependencies.txt

COPY init.sh /init.sh
WORKDIR /var/django-site/
ENTRYPOINT [ "bash", "/init.sh" ]
