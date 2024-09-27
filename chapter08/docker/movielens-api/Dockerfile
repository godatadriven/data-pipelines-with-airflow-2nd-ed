FROM python:3.11-slim

COPY requirements.txt /tmp/requirements.txt
RUN apt-get update && apt-get install unzip && rm -rf /var/lib/apt/lists/*
RUN pip install -r /tmp/requirements.txt && rm -f /tmp/requirements.txt

COPY ml-2023-ratings.zip /

RUN unzip ml-2023-ratings.zip && rm -f ml-2023-ratings.zip && mv /2023-ratings.csv /ratings.csv

EXPOSE 8081

ENTRYPOINT ["python"]
CMD ["/app.py"]
