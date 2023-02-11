FROM python:3.10.6
WORKDIR /app
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./scrapy/* /app/scrapy/
COPY ./script.py /app/
RUN chmod a+x /app/script.py
