FROM python:3.7

COPY . /code/

WORKDIR /code

RUN pwd

RUN ls -a

RUN pip install pipenv

RUN pipenv install --skip-lock