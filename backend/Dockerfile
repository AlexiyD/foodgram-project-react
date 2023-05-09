FROM python:3.8-slim
# Requirements for psycorg2 and script "/app/run_app.sh".
RUN apt-get update &&\
    apt-get upgrade -y &&\
    apt-get install -y libpq-dev gcc netcat
# It also create directory /app.
WORKDIR /app
COPY requirements.txt ./
RUN pip install -U pip &&\
    pip install -r requirements.txt --no-cache-dir
COPY ./foodgram .
#RUN while ! nc -z db 5432; do sleep .5; echo "wait database"; done; echo "connected to the database";
RUN python manage.py migrate;
RUN python manage.py collectstatic --noinput;
ENTRYPOINT [" gunicorn -w 2 -b 0:8000 foodgram.wsgi;"]