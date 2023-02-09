FROM python:3.10.6
WORKDIR /netology
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./netology/* /netology/
COPY ./script.py /netology/
RUN chmod a+x /netology/script.py
