FROM python:3.9

WORKDIR /src

COPY requirements.txt /src
RUN python -m pip install -r requirements.txt

COPY . /src