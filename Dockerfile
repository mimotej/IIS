FROM python:latest

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt
RUN python manage.py db init
EXPOSE 5000
ENTRYPOINT [ "python3" ]
CMD [ "app/__init__.py" ]