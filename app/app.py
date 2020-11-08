from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import logging as logger


logger.basicConfig(level='DEBUG')

app = Flask(__name__)

app.permanent_session_lifetime = timedelta(minutes=30)

app.config['SECRET_KEY'] = 'a4b32a254b543f4d5e44ed255a4b22c1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://flask:password@127.0.0.1/IIS'
app.config['SECRET_KEY'] = '1f3118edada4643f34538ea423d32b21'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
import routes

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
if __name__ == '__main__':
    db.create_all()
    db.session.commit()
    app.run(debug=True, host='0.0.0.0')
