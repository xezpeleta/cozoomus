FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY cozoomus.py /usr/src/app/
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT /entrypoint.sh