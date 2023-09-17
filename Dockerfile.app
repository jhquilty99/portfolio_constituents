# syntax=docker/dockerfile:1
FROM python:3.11.4-slim-buster 
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN pip install .
EXPOSE 5001
CMD ["gunicorn", "-b", ":5001", "wsgi:server"]