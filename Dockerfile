FROM python:3.7.4
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/

RUN pip install -r requirements.txt

ADD . /code/

EXPOSE 8000 80/tcp

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:80", "--log-level", "debug", "wsgi:application", "-w", "4"]
