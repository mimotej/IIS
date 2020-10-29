from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt

from database import *
from datetime import timedelta
import logging as logger
logger.basicConfig(level='DEBUG')

from database import db, app
bcrypt = Bcrypt(app)

app.permanent_session_lifetime = timedelta(minutes=30)

@app.route('/')
def index():
    import pdb; pdb.set_trace()
    return render_template('index.html')

@app.route('/logn', methods=['GET', 'POST'])
def login():
    '''Process data for login'''
    if( request.method == "POST" ):
        if( 'user_id' in session ):
            logger.debug("You are logged in")
        else:
            user = User.query.filter_by(email=request.form['email']).first()
            if user:
                if bcrypt.check_password_hash(user.password, request.form['password']):
                    session['user_id'] = user._id
                    logger.debug("User logged in")
                else:
                    logger.debug("Bad password")
            else:
                logger.debug("User not found")
    return redirect(url_for('index'))

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    '''Process data for sign up'''
    data = request.form
    import pdb; pdb.set_trace()
    if(User.query.filter_by(email=data['email']).first()):
        logger.debug("Email already registered")
    else:
        new_user = User(data['name'], data['surname'], bcrypt.generate_password_hash(data['password']), data['email'], data['phone'])
        db.session.add(new_user)
        db.session.commit()
        logger.debug("New user registered")
    return redirect(url_for('index'))

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
