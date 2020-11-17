import logging as logger
import pickle
from flask import Flask


from flask_bcrypt import Bcrypt
logger.basicConfig(level=logger.DEBUG)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'a4b32a254b543f4d5e44ed255a4b22c1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://flask:Password<3@127.0.0.1/IIS'
app.config['SECRET_KEY'] = '1f3118edada4643f34538ea423d32b21'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class User(db.Model):
    __tablename__ = 'users'
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    phone = db.Column(db.String(50), nullable=False)
    adress = db.Column(db.String(100))
    birth_date = db.Column(db.DateTime)
    isAdmin = db.Column("isAdmin", db.Boolean(), default=False)
    isDoctor = db.Column("isDoctor", db.Boolean(), default=False)
    isInsurance = db.Column("isInsurance", db.Boolean(), default=False)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key == "name":
                self.name = value
            elif key == "surname":
                self.surname = value
            elif key == "password":
                self.password = value
            elif key == "email":
                self.email = value
            elif key == "phone":
                self.phone = value
            elif key == "isInsurance":
                if value == False:
                    self.isInsurance = False
                else:
                    self.isInsurance = True
            elif key == "isAdmin":
                if value == False:
                    self.isAdmin = False
                else:
                    self.isAdmin = True
            elif key == "isDoctor":
                if value == False:
                    self.isDoctor = False
                else:
                    self.isDoctor = True


class HealthProblem(db.Model):
    __tablename__ = 'health_problems'
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(1024))
    state = db.Column(db.String(16), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users._id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users._id'), nullable=False)

    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            if key =="name":
                self.name = value
            elif key == "description":
                self.description = value
            elif key == "state":
                self.state = value
            elif key == "patient_id":
                self.patient_id = value
            elif key == "doctor_id":
                self.doctor_id = value


class ExaminationRequest(db.Model):
     __tablename__ = 'examination_request'
     _id = db.Column("id", db.Integer, primary_key=True)
     name = db.Column("name", db.String(64), nullable=False)
     description = db.Column("description", db.String(1024))
     state = db.Column("state", db.String(16), nullable=False)
     created_by = db.Column("created_by", db.Integer)
     works_on = db.Column("works_on", db.Integer)

     def __init__(self, health_problem_id, name, state, created_by, works_on, description=None):
         self.health_problem_id = health_problem_id
         self.name = name
         self.state = state
         self.created_by = created_by
         self.works_on = works_on
         self.description = description


class MedicalReport(db.Model):
    __tablename__ = 'medical_report'
    _id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1024))
    attachement = db.Column(db.String(1024))
    health_problem = db.Column(db.ForeignKey('HealthProblem.id'), nullable=False)
    author = db.Column(db.ForeignKey('User.id'), nullable=False)
    examination_request = db.Column(db.ForeignKey('ExaminationRequest.id'))

    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            if key == "health_problem":
                self.health_problem=value
            elif key == "author":
                self.author = value
            elif key == "content":
                self.content = value
            elif key == "attachment":
                self.attachement = value
            elif key == "examination_request":
                self.examination_request = value
#Je toto potřeba záznam z vyšetření by měla být zpráva a podání žádosti o proplacení to níže...
class MedicalIntervention(db.Model):
    __tablename__ = 'medical_intervention'
    _id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256))
    executor = db.Column(db.String(256), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __init__(self, executor, price, description=None):
        self.executor = executor
        self.price = price
        self.description = description

class PaymentRequest(db.Model):
    __tablename__ = 'payment_request'
    _id = db.Column(db.Integer, primary_key=True)
    medical_intervention = db.Column(db.Integer, nullable=False)
    creator = db.Column(db.Integer, nullable=False)
    validator = db.Column(db.Integer, nullable=False)
    examination_request = db.Column(db.Integer, nullable=False)
    state = db.Column(db.Integer, nullable=False)
    pay_method = db.Column(db.String(32), nullable=False)

    def __init__(self, medical_intervention, creator, validator,
                 examination_request, state, pay_method):
        self.medical_intervention = medical_intervention
        self.creator = creator
        self.validator = validator
        self.examination_request = examination_request
        self.state = state
        self.pay_method = pay_method
class PaymentTemplate(db.Model):
    __tablename__ = 'payment_template'
    _id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    Price = db.Column(db.Integer, nullable=False)
    Type = db.Column(db.String(255), nullable=False)
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            if key == "name":
                self.Name = value
            elif key == "price":
                self.Price = value
            elif key == "type":
                self.Type = value
db.create_all()
db.session.commit()
