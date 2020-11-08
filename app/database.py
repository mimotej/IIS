from flask_sqlalchemy import SQLAlchemy
from app import app
db = SQLAlchemy()
database.db.create_all()
database.db.session.commit()
class person(db.Model):
    id = db.Column("id_person", db.Integer, primary_key=True)
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