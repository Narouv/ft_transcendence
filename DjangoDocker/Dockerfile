FROM python:latest

RUN python -m pip install Django==5.0.3 psycopg django-environ psycopg2-binary
RUN alias devserv='python manage.py runserver 0.0.0.0:8000'

ENTRYPOINT ["tail", "-f"]