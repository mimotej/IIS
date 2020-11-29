FROM python:latest

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT [ "python3" ]
CMD [ "app/app.py" ]
