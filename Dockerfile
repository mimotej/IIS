#FROM python:3.8

#EXPOSE 5000

#RUN mkdir /app
#WORKDIR /app

#COPY requirements.txt /app/requirements.txt
#RUN pip install -r requirements.txt

#COPY . /app

#CMD python app.py
FROM python:latest

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT [ "python3" ]
CMD [ "app/app.py" ]