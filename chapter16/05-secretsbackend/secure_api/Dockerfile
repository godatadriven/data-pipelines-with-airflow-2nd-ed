FROM python:3.12-slim

RUN pip install Flask~=3.1.1
COPY app.py /app/app.py
RUN chmod +x /app/app.py

EXPOSE 5000

ENTRYPOINT ["python"]
CMD ["/app/app.py"]
