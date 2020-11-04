from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from database import *
from datetime import timedelta
import logging as logger
logger.basicConfig(level='DEBUG')

app = Flask(__name__)
db = SQLAlchemy(app)
db.init_app(app)

app.permanent_session_lifetime = timedelta(minutes=30)

app.config['SECRET_KEY'] = 'a4b32a254b543f4d5e44ed255a4b22c1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Iis2020?@127.0.0.1/IIS'
app.config['SECRET_KEY'] = '1f3118edada4643f34538ea423d32b21'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logn', methods=['GET', 'POST'])
def login():
    '''Process data for login'''
    if( request.method == "POST" ):
        import pdb; pdb.set_trace()
        if( 'user_id' in session ):
            logger.debug("You are logged in")
        else:
            hashed_pass = db.session.query(User.password).where(User.email==request.form['email'])
    return "kokos"

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    '''Process data for sign up'''
    data = request.form
    import pdb; pdb.set_trace()
    if(db.session.query.filter_by(email=data['email']).first()):
        logger.debug("Email already registered")
    else:
        new_user = User(data['name'], data['surname'], data['password'], data['email'], data['phone'])
        db.session.add(new_user)
        db.session.commit()
        logger.debug("New user registered")
        _id = db.session.query.filter_by(email=data['email'].first())
    return 'kokos'

@app.route('/user')
def user():
    return render_template('user.html')


@app.route('/manage_users')
def manage_users():
    return render_template('admin_only/manage_users.html')


@app.route('/paid_action_db')
def paid_action():
    return render_template('insurance_worker/paid_action_db.html')


@app.route('/paid_action_new')
def paid_action_new():
    return render_template('insurance_worker/manage_new_action.html')


@app.route('/health')
def health_problem():
    return render_template('doctor_only/add_health_problem_new_user.html')


@app.route('/health_old')
def health_problem_old():
    return render_template('doctor_only/add_health_problem_registered_user.html')


@app.route('/add_user')
def add_user():
    return render_template('admin_only/add_user.html')


@app.route('/manage_paid_actions')
def manage_paid_actions():
    return render_template('insurance_worker/manage_paid_actions.html')





@app.route('/ticket')
def tickets():
    return render_template('medical_examination_ticket.html')


@app.route('/problem_report')
def medical_report():
    return render_template('not_menu_accessible/problem_report.html')


@app.route('/404')
def not_found_404():
    return render_template('404_not_found.html')


@app.route('/delegate_problem')
def delegate():
    return render_template('doctor_only/delegate_problem.html')


@app.route('/medical_report')
def medical_problem():
    return render_template('not_menu_accessible/medical_report.html')

@app.route('/medical_examinations')
def medical_examinations():
    return render_template('doctor_only/medical_examinations.html')
@app.route('/medical_examination')
def medical_examination():
    return render_template('doctor_only/medical_examination.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='0.0.0.0')
