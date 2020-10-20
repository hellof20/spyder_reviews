FROM python:3.7.8
RUN mkdir -p /src/app
WORKDIR /src/app
COPY requirements.txt /src/app/requirements.txt
COPY scraper.py /src/app/scraper.py
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download ja_core_news_sm
RUN python -m spacy download zh_core_web_sm
CMD [ "python", "scraper.py" ]