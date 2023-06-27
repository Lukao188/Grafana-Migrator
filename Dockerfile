FROM python:latest

WORKDIR /app
COPY ./app /grafana-migrator

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["./app/job.sh"]
