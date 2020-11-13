import logging as logger
logger.basicConfig(level=logger.DEBUG)

from app import app, db
"""
class User(db.Model):
    __tablename__ = 'person'
    Jeste chybi pridat adresu ale pro testovani asi neni tolik nutna jen se nesmi zapomenout!
    _id = db.Column("id_person", db.Integer, primary_key=True)
    name = db.Column("person_name", db.String(50))
    surname = db.Column("surname", db.String(50))
    password = db.Column("person_password", db.String(255))
    email = db.Column("email", db.String(50))
    phone = db.Column("phone_number", db.String(50))
    isAdmin = db.Column("isAdmin", db.Boolean(), default=False)
    isDoctor = db.Column("isDoctor", db.Boolean(), default=False)
    isInsurance = db.Column("isInsurance", db.Boolean(), default=False)
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            if key == "name":
                self.name = value
            elif key == "surname":
                self.surname = value
            elif key == "password":
                self.password = bcrypt.generate_password_hash(value)
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
                    self.isDoctor = True"""
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'IISkokos1999?'
# app.config['MYSQL_DB'] = 'IIS'