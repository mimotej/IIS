from os import TMP_MAX
from flask import Flask, render_template, request, redirect, url_for, session
from database import *
from datetime import timedelta
import logging as logger
from database import db, app

logger.basicConfig(level='DEBUG')
bcrypt = Bcrypt(app)
app.permanent_session_lifetime = timedelta(minutes=30)
app.jinja_env.globals.update(zip=zip)

# List of keys set during session
SESSION_USER_DATA = ['isAdmin', 'isDoctor', 'isInsurance', 'user_id']


@app.route('/')
def index():
    '''Show health problems according to user permissions'''
    if session.get('isAdmin'):
        problems = HealthProblem.query
    elif session.get('isDoctor'):
        problems = HealthProblem.query.filter_by(doctor_id=session['user_id'])
    elif session.get('user_id'):
        problems = HealthProblem.query.filter_by(
            patient_id=session['user_id']
        )
    else:
        problems = []
    return render_template('index.html', problems=problems)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    '''Log out user'''
    for item in SESSION_USER_DATA:
        session.pop(item)
    logger.debug("User logged out")  # TODO replace with flash messages
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Process data for login'''
    if( request.method == "POST" ):
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            if bcrypt.check_password_hash(user.password, request.form['password']):
                session.update(user.login_dict())
                logger.debug("User logged in")  # TODO replace with flash messages
            else:
                logger.debug("Bad password")  # TODO replace with flash messages
        else:
            logger.debug("User not found")  # TODO replace with flash messages
    return redirect(url_for('index'))


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    '''Process data for sign up'''
    data = request.form.to_dict()
    if(User.query.filter_by(email=data['email']).first()):
        logger.debug("Email already registered")  # TODO replace with flash messages
    else:
        data['password'] = bcrypt.generate_password_hash(data['password'])
        add_row(User, **data)
        logger.debug("New user registered")  # TODO replace with flash messages
    return redirect(url_for('index'))

@app.route('/user', methods=['GET', 'POST'])
def user():
    '''Show user info'''
    user = User.query.filter_by(_id=session.get('user_id')).first()
    if request.method == 'POST':
        user.update(**request.form.to_dict())
    # TODO user not logged in scenerio not coverd in user.html
    return render_template('user.html', user=user, my_user=True)

@app.route('/manage_users/<int:id>', methods=['GET', 'POST'])
def redirect_user(id):
    '''Redirect to edit user'''
    return redirect(url_for('update_user', id=id))


@app.route('/manage_users/user/<int:id>')
def update_user(id):
    '''Show and update user info '''
    if session.get('isAdmin') or id == session.get('user_id'):
        user = User.query.filter_by(_id=id).first()
        if request.method == 'POST':
            user.update(**request.form.to_dict())
        # TODO user not logged in scenerio not coverd in user.html
        return render_template('user.html', user=user, my_user=False)
    else:
        redirect(url_for('not_found_404'))

@app.route('/manage_users')
def manage_users():
    '''Manage users (admin only)'''
    return render_template(
            'admin_only/manage_users.html',
            users=permitted_query(User, session.get('isAdmin'))
    )


@app.route('/paid_action_db')
def paid_action():
    return render_template(
            'insurance_worker/paid_action_db.html',
            p_templates=permitted_query(PaymentTemplate,
                                        session.get('isInsurance'))
    )


@app.route('/paid_action_new', methods=['GET', 'POST'])
def paid_action_new():
    if( request.method == "POST" ):
        if session['isAdmin'] or session['isInsurance']:
            add_row(PaymentTemplate, **request.form.to_dict())
            logger.debug("New paid action created")    # TODO replace with flash messages
    return render_template('insurance_worker/manage_new_action.html')

@app.route('/process_request_payment_approved/<int:payment_id>')
def process_request_approved_payment(payment_id):
    print(payment_id)
    return redirect(url_for('index'))

@app.route('/process_request_payment_not_approved/<int:payment_id>')
def process_request_not_approved_payment(payment_id):
    print(payment_id)
    return redirect(url_for('index'))
### ???
@app.route('/health', methods=['GET', 'POST'])
def health_problem():
    if( request.method == "POST" ):
        if session['isAdmin'] or session['isDoctor']:
            data = request.form.to_dict()
            if(User.query.filter_by(email=data['email']).first()):
                logger.debug("User exists")
            else:
                data['password'] = bcrypt.generate_password_hash(data['password'])
                new_user = User(data)
                new_user.isAdmin = False
                new_user.isDoctor = False
                new_user.isInsurance = False
                db.session.add(new_user)
                db.session.commit()
                logger.debug("New user registered")
            new_problem = HealthProblem(data)
            user = User.query.filter_by(email=request.form['email']).first()
            if user:
                new_problem.patient_id = user._id
                new_problem.doctor_id = session['user_id']
                new_problem.name = request.form['name_problem']
                db.session.add(new_problem)
                db.session.commit()
            else:
                logger.debug("User not found")
            return redirect(url_for('health_problem'))
    return render_template('doctor_only/add_health_problem_new_user.html')

### ???
@app.route('/health_old', methods=['GET', 'POST'])
def health_problem_old():
    if( request.method == "POST" ):
        if session['isAdmin'] == True or session['isDoctor']==True:
            data = request.form.to_dict()
            new_problem=HealthProblem(data)
            user = User.query.filter_by(email=request.form['user_email']).first()
            if user:
                new_problem.patient_id = user._id
                new_problem.doctor_id = session['user_id']
                db.session.add(new_problem)
                db.session.commit()
            else:
                logger.debug("User not found")
            return redirect(url_for('health_problem'))
    return render_template('doctor_only/add_health_problem_registered_user.html')


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if session['isAdmin']:
        if request.method == "POST":
            data = request.form.to_dict()
            if(User.query.filter_by(email=data['email']).first()):
                logger.debug("Email already registered")  # TODO replace with flash messages
            else:
                data['password']=bcrypt.generate_password_hash(data['password'])
                add_row(User, **data)
                logger.debug("User registered")  # TODO replace with flash messages
        return render_template('admin_only/add_user.html')
    return redirect(url_for('index'))

### ???
@app.route('/manage_paid_actions')
def manage_paid_actions():
    p_requests = PaymentRequest.query
    p_templates = PaymentTemplate.query
    p_doctor = {}
    templates=[]
    for req in p_requests:
        templates.append(PaymentTemplate.query.filter_by(_id=req.template).first())
        p_doctor[req._id]=User.query.filter_by(_id=req.creator).first().name
    return render_template('insurance_worker/manage_paid_actions.html', p_requests = p_requests, p_templates = p_templates,templates = templates, p_doctor=p_doctor)


@app.route('/ticket',  methods=['GET', 'POST'])
def tickets():
    if request.method == 'POST':
        if session.get('isAdmin') or session.get('isDoctor'):
            problem_id =  request.args.get('p_id')
            data = request.form.to_dict()
            doctor = User.query.filter_by(_id=data.get('received_by')).first()
            if doctor.isDoctor:
                add_row(ExaminationRequest, created_by=session.get('user_id'), state="Not done", health_problem=problem_id, **data)
            else:
                logger.debug("Error: not doctor ID")

    return render_template('medical_examination_ticket.html')


@app.route('/problem_report',  methods=['GET', 'POST'])
def medical_report():
    problem_id =  request.args.get('p_id')
    problem = HealthProblem.query.filter_by(_id=problem_id).first()
    if problem:
        if(session['isAdmin'] or problem.patient_id == session.get('user_id')
            or problem.doctor_id == session.get('user_id')):
            doctor = User.query.filter_by(_id=problem.doctor_id).first()
            if doctor:
                return render_template(
                    'not_menu_accessible/problem_report.html',
                    problem=problem, doctor=doctor.name
                )
    ### TODO Maybe get to previous link?
    

### TODO Maybe make it default route?
@app.route('/404')
def not_found_404():
    return render_template('404_not_found.html')


@app.route('/delegate_problem',  methods=['GET', 'POST'])
def delegate():
    if (request.method == 'POST'):
        problem_id =  request.args.get('p_id')
        problem = HealthProblem.query.filter_by(_id=problem_id).first()
        if problem:
            doctor = User.query.filter_by(_id=request.form['id_doctor']).first()
            if doctor and (session['isAdmin'] or session['isDoctor']):
                logger.debug(doctor._id)
                problem.doctor_id = doctor._id
                ### ???
                db.session.delete(problem)
                db.session.add(problem)
                db.session.commit()
    return render_template('doctor_only/delegate_problem.html')


@app.route('/medical_report',  methods=['GET', 'POST'])
def medical_problem():
    return render_template('not_menu_accessible/medical_report.html')


@app.route('/medical_report_creator/<string:health_problem_id>', methods=['GET', 'POST'])
def medical_report_creator(health_problem_id):
    if session.get('isAdmin') or session.get('isDoctor'):
        if request.method == 'POST':
            data = request.form.to_dict()
            add_row(MedicalReport, author=session.get('user_id'), health_problem=health_problem_id, **data)
        return render_template('not_menu_accessible/medical_report_creator.html')
    return redirect(url_for('/'))


@app.route('/medical_examinations')
def medical_examinations():
    health_problem_names={}
    for request in ExaminationRequest.query:
        health_problem_names[request.id]= ExaminationRequest.query.filter_by(id=request.health_problem_id).first().name
        print(health_problem_names[request.id])
    return render_template('doctor_only/medical_examinations.html',
                           requests=ExaminationRequest.query, health_problem_names=health_problem_names)

### TODO Refactor adding table row
@app.route('/payment_request',  methods=['GET', 'POST'])
def payment_request():
    if request.method == 'POST':
        if session['isAdmin'] or session['isInsurance']:
            data = request.form.to_dict()
            new_payment_request = PaymentRequest(data)
            new_payment_request.creator = session['user_id']
            new_payment_request.examination_request = session['examination_request']
            new_payment_request.template = request.form['template']
            new_payment_request.validator = 1 # je to vzdy 1 <- musi se to nejak upravit at je to korektne
            db.session.add(new_payment_request)
            db.session.commit()
    return render_template('doctor_only/payment_request.html')


@app.route('/medical_examination')
def medical_examination():
    if (session['isAdmin'] or session['isDoctor']):
        request_id =  request.args.get('r_id')
        session['examination_request'] = request_id 
        e_request = ExaminationRequest.query.filter_by(id=request_id).first()
        return render_template('doctor_only/medical_examination.html',
                               e_request=e_request)
    else :
        logger.debug("Error: not admin or doctor")  # TODO replace with flash messages
        return render_template('doctor_only/medical_examination.html',e_request=None)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='0.0.0.0')
