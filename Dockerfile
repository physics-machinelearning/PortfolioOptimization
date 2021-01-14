FROM python:3.7

COPY ./portfolioopt /code/

COPY Pipfile /code/Pipfile

WORKDIR /code

RUN pwd

RUN ls -a

RUN pip install pipenv

RUN pipenv install --skip-lock