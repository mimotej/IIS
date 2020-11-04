import logging as logger
logger.basicConfig(level=logger.DEBUG)

from app import app, db

class User(db.Model):
    __tablename__ = 'person'

    _id = db.Column("id_person", db.Integer, primary_key=True)
    name = db.Column("person_name", db.String(50))
    surname = db.Column("surname", db.String(50))
    password = db.Column("person_password", db.String(255))
    email = db.Column("email", db.String(50))
    phone = db.Column("phone_number", db.String(50))

    def __init__(self, name, surname, password, email, phone):
        self.name = name
        self.surname = surname
        self.password = password
        self.email = email
        self.phone = phone

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'IISkokos1999?'
# app.config['MYSQL_DB'] = 'IIS'