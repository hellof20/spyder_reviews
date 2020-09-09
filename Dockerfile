FROM python:3.7.8
RUN mkdir -p /src/app
WORKDIR /src/app
COPY requirements.txt /src/app/requirements.txt
COPY app.csv /src/app/app.csv
COPY mysql.csv /src/app/mysql.csv
COPY scraper.py /src/app/scraper.py
RUN pip install -r requirements.txt
CMD [ "python", "scraper.py" ]
