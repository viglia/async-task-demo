FROM python:3.7

WORKDIR /usr/src/app
COPY job_consumer.py .
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "job_consumer.py"]


