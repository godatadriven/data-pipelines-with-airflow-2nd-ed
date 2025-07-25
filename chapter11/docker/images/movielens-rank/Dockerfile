FROM python:3.12-slim

RUN pip install click==8.1.7 pandas==2.2.2

COPY scripts/rank_movies.py /usr/local/bin/rank-movies
RUN chmod +x /usr/local/bin/rank-movies

ENV PATH="/usr/local/bin:${PATH}"
