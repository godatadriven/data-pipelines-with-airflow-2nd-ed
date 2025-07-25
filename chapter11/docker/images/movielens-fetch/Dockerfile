FROM python:3.12-slim

RUN python -m pip install click==8.1.7 requests==2.32.3

COPY scripts/fetch_ratings.py /usr/local/bin/fetch-ratings
RUN chmod +x /usr/local/bin/fetch-ratings

ENV PATH="/usr/local/bin:${PATH}"
