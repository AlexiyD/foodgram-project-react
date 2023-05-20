FROM python:3.8

WORKDIR /app
COPY requirements.txt ./
RUN pip install -U pip &&\
 pip install -r requirements.txt --no-cache-dir
COPY ./foodgram /app
CMD ["gunicorn -w 2 -b 0:8000 foodgram.wsgi;"]
