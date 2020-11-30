import logging as logger
import pickle
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_sqlalchemy import event
from werkzeug.utils import secure_filename
import os
import random
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads', 'reports')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_INT_32 = 2147483647-1

logger.basicConfig(level=logger.DEBUG)  # Set logger for whatever reason
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/IIS'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://xdrlam00:Mimak123@mysqltestingxdrlam.mysql.database.azure.com/testdbmysql' #třeba zakomentovat a odkomentovat lokální a upravit přihlašovací údaje
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'a4b32a254b543f4d5e44ed255a4b22c1'
app.config['SECRET_KEY'] = '1f3118edada4643f34538ea423d32b21'


class User(db.Model):
    __tablename__ = 'users'
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    phone = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100))
    city = db.Column(db.String(255))
    birthNumber = db.Column(db.String(255))
    isAdmin = db.Column("isAdmin", db.Boolean(), default=False)
    isDoctor = db.Column("isDoctor", db.Boolean(), default=False)
    isInsurance = db.Column("isInsurance", db.Boolean(), default=False)

    def __init__(self, data):
        self._id = gen_id(User)
        self.name = data.get('name')
        self.surname = data.get('surname')
        self.password = data.get('password')
        self.email = data.get('email')
        self.phone = data.get('phone')
        self.address = data.get('address')
        self.city = data.get('city')
        self.birthNumber = data.get('birthnumber')
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
        self.city = kwargs['city'] if kwargs.get('city') else self.city
        self.isAdmin = kwargs['isadmin'] == "True"  if kwargs.get('isadmin') else self.isAdmin
        self.isDoctor = kwargs['isdoctor'] =="True" if kwargs.get('isdoctor') else self.isDoctor
        self.isInsurance = kwargs['isinsurance'] == "True"  if kwargs.get('isinsurance') else self.isInsurance
        logger.debug(kwargs)
        db.session.commit()

     
    def get_url(self):
        return 'Document.location = "/"'

    def delete(self, sub_doc_id=False):
        if self.isDoctor or self.isAdmin:
            if not User.query.filter_by(_id=sub_doc_id).first():
                logger.debug("Provided substitute doctor id invalid")  # TODO flash message?
                return False
            else:
                query = HealthProblem.query.filter_by(doctor_id=self._id).all()
                for q in query:
                    q.doctor_id = sub_doc_id
                query = ExaminationRequest.query.filter_by(created_by=self._id).all()
                for q in query:
                    if q.created_by == self._id:
                        q.created_by = sub_doc_id
                query = ExaminationRequest.query.filter_by(received_by=self._id).all()
                for q in query:
                    if q.received_by == self._id:
                        q.received_by = None
                query = MedicalReport.query.filter_by(author=self._id).all()
                for q in query:
                    q.author = sub_doc_id
                query = PaymentRequest.query.filter_by(creator=self._id).all()
                for q in query:
                    q.creator = sub_doc_id
        if self.isInsurance or self.isAdmin:
            query = PaymentRequest.query.filter_by(creator=self._id).all()
            for q in query:
                q.creator = None
            query = PaymentRequest.query.filter_by(validator=self._id).all()
            for q in query:
                q.validator = None
        query = HealthProblem.query.filter_by(patient_id=self._id).all()
        for q in query:
            q.delete()
        db.session.commit()
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
        self._id = gen_id(HealthProblem)
        self.name = data.get('name')
        self.description = data.get('description')
        self.state = data.get('state')
        self.patient_id = data.get('patient_id')
        self.doctor_id = data.get('doctor_id')

    def delete(self):
        delete_query(MedicalReport.query.filter_by(health_problem=self._id))
        delete_query(ExaminationRequest.query.filter_by(health_problem_id=self._id))

class ExaminationRequest(db.Model):
    __tablename__ = 'examination_request'
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column("name", db.String(64), nullable=False)
    description = db.Column("description", db.String(1024))
    state = db.Column("state", db.String(16), nullable=False)
    created_by = db.Column("created_by", db.Integer,
                           db.ForeignKey('users._id'), nullable=False)
    received_by = db.Column("received_by", db.Integer,
                            db.ForeignKey('users._id'), nullable=True)
    health_problem_id = db.Column(db.ForeignKey('health_problems._id'),
        nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, data):
        self._id = gen_id(ExaminationRequest)
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
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, data):
        self._id = gen_id(MedicalReport)
        self.Name= data.get('Name')
        self.health_problem = data.get('health_problem_id')
        self.author = data.get('author')
        self.content = data.get('content')
        self.attachment_name = data.get('attachment')
        self.examination_request = data.get('examination_request')

class PaymentRequest(db.Model):
    __tablename__ = 'payment_request'
    _id = db.Column(db.Integer, primary_key=True)
    template = db.Column("payment_template", db.Integer,
                         db.ForeignKey('payment_template._id'), nullable=False)
    creator = db.Column("creator", db.Integer, db.ForeignKey('users._id'))
    validator = db.Column("validator", db.Integer, db.ForeignKey('users._id'))
    examination_request = db.Column(
        "examination_request", db.Integer,
        db.ForeignKey('examination_request._id'), nullable=True
    )
    state = db.Column(db.String(256), nullable=True)

    def __init__(self, data):
        self._id = gen_id(PaymentRequest)
        self.template = data.get('template')
        self.creator = data.get('creator')
        self.validator = data.get('validator')
        self.examination_request = data.get('examination_request')
        self.state = data.get('state', 'Čekající')


class PaymentTemplate(db.Model):
    __tablename__ = 'payment_template'
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(255), nullable=False)

    def __init__(self, data):
        self._id = gen_id(PaymentTemplate)
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

def delete_query(query):
    for q in query:
        db.session.delete(q)
    db.session.commit()


def gen_id(Table):
    id = random.randint(1, MAX_INT_32)
    while Table.query.filter_by(_id=id).first():
        id = random.randint(1, MAX_INT_32)
    return id

def filter(Table, **kwargs):
    return Table.query.filter_by(**kwargs).all()

db.create_all()
db.session.commit()
