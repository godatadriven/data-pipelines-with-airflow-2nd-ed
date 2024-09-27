FROM python:3.12-slim

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm -f /tmp/requirements.txt

COPY app.py /

EXPOSE 8081

ENTRYPOINT ["uvicorn"]
CMD ["--host", "0.0.0.0", "--port", "8081", "app:app"]
