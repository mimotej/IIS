import logging as logger
import pickle
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads', 'reports')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

logger.basicConfig(level=logger.DEBUG)  # Set logger for whatever reason
app = Flask(__name__)
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'a4b32a254b543f4d5e44ed255a4b22c1'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Iis2020?@127.0.0.1/IIS'
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
    address = db.Column(db.String(100))
    birth_date = db.Column(db.DateTime)
    isAdmin = db.Column("isAdmin", db.Boolean(), default=False)
    isDoctor = db.Column("isDoctor", db.Boolean(), default=False)
    isInsurance = db.Column("isInsurance", db.Boolean(), default=False)

    def __init__(self, data):
        self.name = data.get('name')
        self.surname = data.get('surname')
        self.password = data.get('password')
        self.email = data.get('email')
        self.phone = data.get('phone')
        self.isInsurance = data.get('isInsurance') == "True"
        self.isAdmin = data.get('isAdmin') == "True"
        self.isDoctor = data.get('isDoctor') == "True"
        self.url = self.get_url
    
    def login_dict(self):
        return {
            'user_id': self._id,
            'isAdmin': self.isAdmin,
            'isDoctor': self.isDoctor,
            'isInsurance': self.isInsurance
        }
    
    def update(self, **kwargs):
        self.name = kwargs['name'] if kwargs.get('name') else self.name
        self.surname = kwargs['surname'] if kwargs.get('surname') else self.surname
        self.email = kwargs['email'] if kwargs.get('email') else self.email
        self.phone = kwargs['phone'] if kwargs.get('phone') else self.phone
        self.address = kwargs['address'] if kwargs.get('address') else self.address
        self.isAdmin == kwargs['isadmin'] == "True"  if kwargs.get('isadmin') else self.isAdmin
        self.isDoctor = kwargs['isdoctor'] =="True" if kwargs.get('isdoctor') else self.isDoctor
        self.isInsurance == kwargs['isinsurance'] == "True"  if kwargs.get('isinsurance') else self.isAdmin
        logger.debug(kwargs)
        db.session.commit()

    def get_url(self):
        return 'Document.location = "/"'  # manage_users/user/" + str(self._id) + "';"
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        logger.debug("User deleted, name: " + self.name)


class HealthProblem(db.Model):
    __tablename__ = 'health_problems'
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(1024))
    state = db.Column(db.String(16), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users._id'),
                           nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users._id'),
                          nullable=False)

    def __init__(self, data):
        self.name = data.get('name')
        self.description = data.get('description')
        self.state = data.get('state')
        self.patient_id = data.get('patient_id')
        self.doctor_id = data.get('doctor_id')


class ExaminationRequest(db.Model):
    __tablename__ = 'examination_request'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("name", db.String(64), nullable=False)
    description = db.Column("description", db.String(1024))
    state = db.Column("state", db.String(16), nullable=False)
    created_by = db.Column("created_by", db.Integer,
                           db.ForeignKey('users._id'), nullable=False)
    received_by = db.Column("received_by", db.Integer,
                            db.ForeignKey('users._id'), nullable=False)
    health_problem_id = db.Column(
        "health_problem_id", db.Integer, db.ForeignKey('health_problems._id'),
        nullable=False)

    def __init__(self, data):
        self.health_problem_id = data.get('health_problem')
        self.name = data.get('name')
        self.state = data.get('state')
        self.created_by = data.get('created_by')
        self.description = data.get('description')
        self.received_by = data.get('receiver')

class MedicalReport(db.Model):
    __tablename__ = 'medical_report'
    _id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(1024))
    content = db.Column(db.String(2048))
    attachment_name = db.Column(db.String(1024))
    health_problem = db.Column(db.ForeignKey('health_problems._id'),
                               nullable=False)
    author = db.Column(db.ForeignKey('users._id'), nullable=False)
    examination_request = db.Column("health_problem_id", db.Integer,
                                    db.ForeignKey('health_problems._id'),
                                    nullable=True)

    def __init__(self, data):
        self.Name= data.get('Name')
        self.health_problem = data.get('health_problem_id')
        self.author = data.get('author')
        self.content = data.get('content')
        self.attachment_name = data.get('attachment')
        self.examination_request = data.get('examination_request')


# Je toto potřeba záznam z vyšetření by měla být zpráva a podání žádosti
# o proplacení to níže... Asi to tu nemá být ale zatím to tu nechám projistotu
class MedicalIntervention(db.Model):
    __tablename__ = 'medical_inervention'
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
    # žádost na konkrétní typ zákroku
    # medical_intervention = db.Column("medical_intervention", db.Integer,
    #   db.ForeignKey('payment_template._id'), nullable=True)
    template = db.Column("payment_template", db.Integer,
                         db.ForeignKey('payment_template._id'), nullable=False)
    creator = db.Column("creator", db.Integer, db.ForeignKey('users._id'),
                        nullable=False)
    validator = db.Column("validator", db.Integer, db.ForeignKey('users._id'),
                          nullable=False)
    examination_request = db.Column(
        "examination_request", db.Integer,
        db.ForeignKey('examination_request.id'), nullable=False
    )
    state = db.Column(db.String(256), nullable=True)

    def __init__(self, data):
        self.template = data.get('template')
        self.creator = data.get('creator')
        self.validator = data.get('validator')
        self.examination_request = data.get('examination_request')
        self.state = data.get('state', 'waiting')
        # self.medical_intervention = data.get('medical_intervention')


class PaymentTemplate(db.Model):
    __tablename__ = 'payment_template'
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(255), nullable=False)

    def __init__(self, data):
        self.name = data.get('name')
        self.price = data.get('price')
        self.type = data.get('type')


def permitted_query(table, permission):
    '''Return all table rows if permission granted'''
    # In case of direct access, show empty list
    value = []
    if permission:
        value = table.query
    if not value:
        # In case error occures on DB side
        value = []
    return value


def add_row(Table, **kwargs):
    '''Add row to table'''
    row_instance = Table(kwargs)
    db.session.add(row_instance)
    db.session.commit()


db.create_all()
db.session.commit()
